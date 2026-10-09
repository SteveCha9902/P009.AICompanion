from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class InteractionSessionState(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    RESUMABLE = "RESUMABLE"
    ENDED = "ENDED"

class InteractionSession(Base):
    __tablename__ = "interaction_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    
    state = Column(Enum(InteractionSessionState), nullable=False, default=InteractionSessionState.ACTIVE)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_interaction_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
class PendingInteraction(Base):
    __tablename__ = "pending_interactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    
    proactive_event_id = Column(String, ForeignKey("proactive_events.id"), nullable=True)
    
    intent = Column(String, nullable=False, comment="e.g. follow_up_on_presentation")
    context_data = Column(String, nullable=True, comment="JSON string with required context")
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
