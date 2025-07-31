from sqlalchemy import Column, TIMESTAMP, text, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class Message(Base):
    __tablename__ = "messages" 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True)
    sender = Column(Text, nullable=False) # 'user' or 'bot'
    content = Column(JSON, nullable=False) # JSONB in PostgreSQL, will store {"text": "..."}
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    chat_session = relationship("ChatSession", back_populates="messages")
