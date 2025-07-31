
from langchain_core.language_models import BaseChatModel
from fastapi import HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from typing import List, Tuple
from uuid import UUID
from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from app.models.chat_session import ChatSession
from sqlalchemy.orm import relationship, selectinload
load_dotenv()


#store history messages and summary
class SummaryHistory:
    def __init__(
        self,
        llm: BaseChatModel,
        max_token_limit: int = 100,
        initial_summary: str = "",
        initial_history: List[BaseMessage] = None,
        initial_summary_count: int = 0
    ):
        self.llm = llm
        self.chat_history: List[BaseMessage] = initial_history or []
        self.summary = initial_summary
        self.max_token_limit = max_token_limit
        self.summary_count = initial_summary_count

    def save_context(self, input: str, output: str):
        print(f"User: {input}")
        print(f"AI: {output}")

        self.chat_history.append(HumanMessage(content=input))
        self.chat_history.append(AIMessage(content=output))

        if self._get_token_count() > self.max_token_limit:
            self._summarize()

    def load_memory_variables(self) -> dict:
        history_str = self.summary + "\n" + self._get_formatted_history()
        return {"history": history_str.strip()}

    def _get_token_count(self) -> int:
        return sum(len(m.content.split()) for m in self.chat_history)

    def _get_formatted_history(self) -> str:
        return "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in self.chat_history
        )

    def _summarize(self):
        print(f"\n📌 [Tóm tắt lần {self.summary_count + 1}] Đang thực hiện tóm tắt do vượt quá giới hạn token...")

        prompt = f"""Tóm tắt cuộc hội thoại sau bằng tiếng Việt, ngắn gọn và rõ ý:\n{self._get_formatted_history()}"""
        stream = self.llm.stream([HumanMessage(content=prompt)])

        summary_parts = []
        for chunk in stream:
            print(chunk.content, end="", flush=True)
            summary_parts.append(chunk.content)

        self.summary += f"\n📝 [Tóm tắt lần {self.summary_count + 1}]: {''.join(summary_parts).strip()}\n"
        self.chat_history = []
        self.summary_count += 1
        print(f"\n✅ Tóm tắt hoàn tất.\n")

async def get_session_memory(
    session_id: UUID,
    db: AsyncSession,
    current_user_id: UUID,
    llm_instance: BaseChatModel,
    max_token_limit: int = 100
) -> Tuple[SummaryHistory, ChatSession]:
    """
    Loads existing chat session and messages to reconstruct HistorySummary
    .
    Returns the memory instance and the chat session ORM object.
    """
    stmt_session = select(ChatSession).where(
    ChatSession.id == session_id,
    ChatSession.user_id == current_user_id
).options(
    selectinload(ChatSession.messages)
)

    result_session = await db.execute(stmt_session)
    chat_session = result_session.scalar_one_or_none()

    if not chat_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found or not authorized")

    existing_messages = sorted(chat_session.messages, key=lambda msg: msg.timestamp)

    messages_for_memory: List[BaseMessage] = []
    for msg in existing_messages:
        message_text = msg.content.get('text', '') if isinstance(msg.content, dict) else str(msg.content)
        if msg.sender == "user":
            messages_for_memory.append(HumanMessage(content=message_text))
        elif msg.sender == "bot":
            messages_for_memory.append(AIMessage(content=message_text))

    initial_summary = chat_session.summary.get('text', '') if isinstance(chat_session.summary, dict) else ""
    initial_summary_count = initial_summary.count("Tóm tắt lần")


    memory = SummaryHistory(
        llm=llm_instance,
        max_token_limit=max_token_limit,
        initial_summary=initial_summary,
        initial_history=messages_for_memory,
        initial_summary_count=initial_summary_count
    )
    return memory, chat_session


