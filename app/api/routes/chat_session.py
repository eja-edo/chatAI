from fastapi import APIRouter, Depends, status, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from uuid import UUID
from app.api.deps import get_db
from app.models.user import User
from app.schemas.chat_session import ChatSessionOut
from app.schemas.message import MessageCreate, MessageOut
from app.core.security import get_current_user
from app.crud.chat_session import create_session, get_sessions, get_one_session, get_all_messages, create_messages, websocket_chat
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/create-chat-session", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
                        current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """Create a new chat section"""
    return await create_session(current_user, db)

@router.get("/get-chat-sessions", response_model=List[ChatSessionOut], status_code=status.HTTP_200_OK)
async def get_chat_sessions(
                            db: Session = Depends(get_db),
                            current_user : User = Depends(get_current_user)):
    """Retrieve all sessions belong to the current user"""
    return await get_sessions(db, current_user)

@router.get("/{session_id}", response_model=ChatSessionOut, status_code=status.HTTP_200_OK)
async def get_chat_session(session_id : UUID,
                            current_user : User = Depends(get_current_user),
                            db : Session = Depends(get_db)):
    """Retrieve the exact session you want to find of the current user"""
    return await get_one_session(session_id, current_user, db)

@router.post("/{session_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message_and_get_bot_response(
    session_id: UUID,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
   return await create_messages(session_id, message, current_user, db)

@router.get("/{session_id}/messages", response_model=List[MessageOut])
async def get_messages_for_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all messages for a specific chat session.
    Ensures the session belongs to the current user for authorization.
    """
    return await get_all_messages(session_id, current_user, db)



#websocket endpoint
active_connections: Dict[UUID, List[WebSocket]] = {}

@router.websocket("/ws/{session_id}/")
async def websocket_endpoint(websocket: WebSocket, session_id: UUID):
    return await websocket_chat(websocket,session_id)