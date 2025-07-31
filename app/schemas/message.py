from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class MessageContent(BaseModel):
    text: str

class MessageCreate(BaseModel):
    sender: str = Field(..., pattern="^(user|bot)$")
    content: MessageContent

class MessageOut(MessageCreate):
    id: UUID
    session_id: Optional[UUID]
    timestamp: datetime

    class Config:
        from_attributes = True