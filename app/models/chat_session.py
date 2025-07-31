from sqlalchemy import Column, TIMESTAMP, text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions" 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    summary = Column(JSONB, nullable=True)
    started_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    ended_at = Column(TIMESTAMP, nullable=True)

    owner = relationship("User", back_populates="session")
    messages = relationship("Message", back_populates="chat_session", cascade="all, delete-orphan")