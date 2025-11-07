from sqlalchemy import Column, ForeignKey, DateTime, Integer, String, Text, JSON, func
from sqlalchemy.orm import relationship
import enum
from app.db.base_model import BaseModel


class SenderTypeEnum(str, enum.Enum):
    PATIENT = "patient"
    AI_AGENT = "ai_agent"
    HUMAN_AGENT = "human_agent"

class ConversationStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    ESCALATED = "escalated"
    CLOSED = "closed"

class Conversation(BaseModel):
    __tablename__ = "conversations"
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    status = Column(String(50), default=ConversationStatusEnum.ACTIVE.value, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient", backref="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(String(), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)  # optional: attachments, AI model info, etc.

    conversation = relationship("Conversation", back_populates="messages")