from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ChatSessionBase(BaseModel):
    summary: Optional[dict] = None # Changed to str to store the summary string

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionOut(ChatSessionBase):
    id: UUID
    user_id: Optional[UUID]
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True