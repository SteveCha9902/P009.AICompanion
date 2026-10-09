from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = lambda dim: String
import uuid
import enum

class MemoryType(str, enum.Enum):
    FACT = "FACT"
    EVENT = "EVENT"
    PERSONAL_FACT = "PERSONAL_FACT"
    PREFERENCE = "PREFERENCE"
    DISLIKE = "DISLIKE"
    INTEREST = "INTEREST"
    HABIT = "HABIT"
    GOAL = "GOAL"
    IMPORTANT_EVENT = "IMPORTANT_EVENT"
    RELATIONSHIP_FACT = "RELATIONSHIP_FACT"
    EMOTIONAL_MEMORY = "EMOTIONAL_MEMORY"
    CHARACTER_INTERPRETATION = "CHARACTER_INTERPRETATION"


class MemorySource(str, enum.Enum):
    USER_EXPLICIT = "USER_EXPLICIT"
    USER_CONFIRMED = "USER_CONFIRMED"
    INFERRED = "INFERRED"
    IMPORTED = "IMPORTED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"

class MemoryKind(str, enum.Enum):
    PERSISTENT = "PERSISTENT"
    TEMPORARY = "TEMPORARY"
    EPISODIC = "EPISODIC"

class MemoryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DELETED = "DELETED"

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    
    type = Column(Enum(MemoryType), nullable=False)
    source = Column(Enum(MemorySource), nullable=False)
    kind = Column(Enum(MemoryKind), nullable=False, default=MemoryKind.PERSISTENT)
    status = Column(Enum(MemoryStatus), nullable=False, default=MemoryStatus.ACTIVE)
    
    content = Column(String, nullable=False)
    subject = Column(String, nullable=True) # e.g. "camera"
    entity = Column(String, nullable=True) # e.g. "Fujifilm"
    polarity = Column(String, nullable=True) # positive, negative, neutral

    importance = Column(Integer, default=50, nullable=False) # 0-100
    confidence = Column(Float, default=1.0, nullable=False) # 0.0-1.0
    
    source_message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    source_conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    
    embedding = Column(Vector(1536), nullable=True) # Assume OpenAI 1536-dim

    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    companion = relationship("Companion")
