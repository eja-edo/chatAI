import os
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=settings.GEMINI_API_KEY, # Use the key from settings
    temperature=0.7,
    model_kwargs={"streaming": True},
)

async def get_llm_response(prompt_messages: List[BaseMessage]) :
    """
   
    Tương tác với Mô hình Ngôn ngữ Lớn (LLM) để nhận phản hồi.

    Args:
        prompt_messages: Danh sách các đối tượng BaseMessage của LangChain 
                     (HumanMessage, AIMessage) đại diện cho lịch sử hội thoại 
                     và lời nhắc hiện tại.

    Returns:
        Chuỗi nội dung phản hồi của bot đã được nối lại.


    """
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "Google API Key is not set. Please set the GOOGLE_API_KEY "
            "environment variable or update it in core/config.py."
        )

    full_response_content = ""
    # try:
        # # Stream the response from the LLM
        # stream = llm.stream(prompt_messages)
        # for chunk in stream:
        #     full_response_content += chunk.content

    async for chunk in llm.astream(prompt_messages):

        yield chunk
    # except Exception as e:
    #     # Log the error and re-raise or handle appropriately
    #     print(f"Error calling LLM: {e}")
    #     raise

    # return full_response_content
