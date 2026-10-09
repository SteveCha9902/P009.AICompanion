from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class ProactiveTriggerType(str, enum.Enum):
    RETURNED_USER = "RETURNED_USER"
    LONG_ABSENCE = "LONG_ABSENCE"
    CONVERSATION_CONTINUATION = "CONVERSATION_CONTINUATION"
    TIME_BASED = "TIME_BASED"
    # Future integration types
    # EMOTIONAL_CONTEXT = "EMOTIONAL_CONTEXT"
    # SYSTEM_EVENT = "SYSTEM_EVENT"
    
class ProactiveDecision(str, enum.Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"

class ProactiveEvent(Base):
    __tablename__ = "proactive_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    
    trigger_type = Column(Enum(ProactiveTriggerType), nullable=False)
    trigger_source = Column(String, nullable=True) # E.g., "scheduler", "heartbeat"
    
    decision = Column(Enum(ProactiveDecision), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    decision_reason = Column(String, nullable=True)
    
    # Snapshots for future reasoning and explainability
    selected_memory_ids = Column(JSON, default=list) # Array of memory IDs
    relationship_snapshot = Column(JSON, default=dict) # { trust: 0.8, level: "CLOSE" }
    emotion_snapshot = Column(JSON, default=dict) # { primary: "JOY", valence: 0.8 }
    
    generated_message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    
    # User reaction loop
    user_responded = Column(Boolean, nullable=True)
    response_delay_seconds = Column(Integer, nullable=True)
    dismissed = Column(Boolean, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class ProactiveSettings(Base):
    __tablename__ = "proactive_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), unique=True, index=True, nullable=False)
    
    enabled = Column(Boolean, nullable=False, default=True)
    daily_limit = Column(Integer, nullable=False, default=3)
    cooldown_minutes = Column(Integer, nullable=False, default=120)
    
    quiet_hours_start = Column(String, nullable=False, default="23:00")
    quiet_hours_end = Column(String, nullable=False, default="07:00")
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
