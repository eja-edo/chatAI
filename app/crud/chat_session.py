from fastapi.websockets import WebSocketState
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.message import MessageCreate
from app.api.deps import get_db
from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.user import User
from app.core.security import get_ws_current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from app.chatbot.memory import get_session_memory
from uuid import UUID
from app.chatbot.llm_management import llm, get_llm_response
from langchain_core.messages import HumanMessage
from typing import Dict, List

active_connections: Dict[UUID, List[WebSocket]] = {}
#websocket endpoint
async def websocket_chat(websocket : WebSocket, session_id : UUID):
    """websocket endpoint for realtime chat"""
    await websocket.accept()

    # Manually handle dependencies
    db_gen = get_db()
    db: AsyncSession = await db_gen.__anext__()
    try:
        current_user = await get_ws_current_user(websocket)
    except Exception as e:
        await websocket.close(code=1008)
        await db_gen.aclose()
        return
    
    if not current_user:
        await websocket.close(code=1008)
        await db_gen.aclose()
        return

    # Confirm session ownership
    stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    result = await db.execute(stmt)
    chat_session = result.scalar_one_or_none()
    if not chat_session:
        await websocket.close(code=1008)
        await db_gen.aclose()
        return

    # Add connection to pool
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)

    try:
        while True:
            # Receive user message
            data = await websocket.receive_json()
            user_text = data.get("text")
            if not user_text:
                continue

            # Load memory & context
            memory, _ = await get_session_memory(
                session_id=session_id,
                db=db,
                current_user_id=current_user.id,
                llm_instance=llm,
                max_token_limit=100
            )
            history = memory.load_memory_variables()["history"]
            print(type(history))
            # Generate bot response
            try:
                response_chunks = []
                async for rep_chunk in get_llm_response(history, user_text):
                   if websocket.client_state != WebSocketState.CONNECTED:
                        break
                   await websocket.send_text(rep_chunk.content)
                   response_chunks.append(rep_chunk.content)

                full_response = "".join(response_chunks)
            except Exception as e:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({"error": f"LLM error: {str(e)}"})
                continue

            # Save both messages
            user_msg = Message(session_id=session_id, sender="user", content={"text": user_text})
            bot_msg = Message(session_id=session_id, sender="bot", content={"text": full_response})
            db.add_all([user_msg, bot_msg])
            await db.flush()

            # Save to memory (summary update)
            memory.save_context(user_text, full_response)
            chat_session.summary = {"text": memory.summary}
            await db.commit()

            disconnected = [
                conn for conn in active_connections[session_id]
                if conn.client_state != WebSocketState.CONNECTED
            ]
            # Clean up any disconnected clients
            for conn in disconnected:
                if conn in active_connections[session_id]:
                    active_connections[session_id].remove(conn)

    except WebSocketDisconnect:
        active_connections[session_id].remove(websocket)
        if not active_connections[session_id]:
            del active_connections[session_id]

    finally:
        await db_gen.aclose()



async def create_session(current_user : User,
                         db: AsyncSession):
    """Create a new chat session"""
    try:
        db_session = ChatSession(user_id = current_user.id)
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something went wrong with the creation of session: {e}")
    
async def create_messages(session_id : UUID,
                          message: MessageCreate,
                          current_user : User,
                          db: AsyncSession):
    """Process messages in a chat session"""
    memory, chat_session = await get_session_memory(
        session_id,
        db,
        current_user.id,
        llm,
        max_token_limit= 100
    )

    converssation_context = memory.load_memory_variables()["history"]
    prompt_messages = [
        HumanMessage(content= converssation_context),
        HumanMessage(content= message.content.text)
    ]

    bot_response = ""
    try:
        bot_response = await get_llm_response(prompt_messages)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM error: {e}")

    try:
        user_db_message = Message(
            session_id = session_id,
            sender= "user",
            content = {"text" : message.content.text}
        )
        db.add(user_db_message)
        await db.flush()

        bot_db_message = Message(
            session_id = session_id,
            sender = "bot",
            content = {"text" : bot_response}
        )
        db.add(bot_db_message)
        await db.flush()

        memory.save_context(message.content.text, bot_response)

        chat_session.summary = {"text" : memory.summary}
        await db.commit()
        await db.refresh(user_db_message)
        return bot_db_message
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error at creating message: {e}")

async def get_sessions(db: AsyncSession, current_user: User):
    """Retrieve all sessions of this specific user"""

    try:
        stmt = select(ChatSession).where(ChatSession.user_id == current_user.id).order_by(ChatSession.started_at.desc())
        results = await db.execute(stmt)
        sessions = results.scalars().all()
        
        return sessions
    
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error while fetching sessions : {e}")
    
async def get_one_session(session_id : UUID,
                           current_user : User,
                           db : AsyncSession):
    """Retrive the exact session requested by specific user"""
    try:
        stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session Not Found")
        return session
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while fetching session: {e}")
    
async def get_all_messages(session_id : UUID,
                           current_user : User,
                           db : AsyncSession):
    """Retrive all messages for a specific chat session belongs to the current user"""
    try:
        stmt = (select(Message)
                .join(ChatSession, Message.session_id == ChatSession.id)
                .where(
                    Message.session_id == session_id,
                    ChatSession.user_id == current_user.id
                )
        ).order_by(Message.timestamp.asc())

        result = await db.execute(stmt)
        messages = result.scalars().all()

        return messages
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while fetching messages {e}")