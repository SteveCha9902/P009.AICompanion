from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class PresenceStateEnum(str, enum.Enum):
    OFFLINE = "OFFLINE"
    IDLE = "IDLE"
    AVAILABLE = "AVAILABLE"
    ENGAGED = "ENGAGED"
    AWAY = "AWAY"
    SLEEPING = "SLEEPING"

class PresenceState(Base):
    __tablename__ = "presence_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), unique=True, index=True, nullable=False)
    
    state = Column(Enum(PresenceStateEnum), nullable=False, default=PresenceStateEnum.AVAILABLE)
    
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    companion = relationship("Companion")
