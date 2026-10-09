from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class EmotionType(str, enum.Enum):
    JOY = "JOY"
    SADNESS = "SADNESS"
    ANGER = "ANGER"
    FEAR = "FEAR"
    SURPRISE = "SURPRISE"
    CALM = "CALM"
    CURIOSITY = "CURIOSITY"
    AFFECTION = "AFFECTION"
    FRUSTRATION = "FRUSTRATION"
    EMPATHY = "EMPATHY"
    TENSION = "TENSION"
    NEUTRAL = "NEUTRAL"

class EmotionState(Base):
    __tablename__ = "emotion_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), unique=True, index=True, nullable=False)
    
    primary_emotion = Column(Enum(EmotionType), nullable=False, default=EmotionType.CALM)
    secondary_emotion = Column(Enum(EmotionType), nullable=True)
    
    valence = Column(Float, nullable=False, default=0.0) # -1.0 to 1.0
    arousal = Column(Float, nullable=False, default=0.0) # 0.0 to 1.0
    warmth = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0 (Current Emotional Activation)
    engagement = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0
    tension = Column(Float, nullable=False, default=0.0) # 0.0 to 1.0
    
    confidence = Column(Float, nullable=False, default=1.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_trigger_at = Column(DateTime(timezone=True), nullable=True)
    
    companion = relationship("Companion")

class EmotionEvent(Base):
    __tablename__ = "emotion_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    
    trigger = Column(String, nullable=True)
    event_type = Column(String, nullable=True) # e.g. "user_shared_success"
    
    previous_state = Column(Enum(EmotionType), nullable=False)
    new_state = Column(Enum(EmotionType), nullable=False)
    
    intensity = Column(Float, nullable=False, default=0.0)
    confidence = Column(Float, nullable=False, default=1.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    companion = relationship("Companion")
