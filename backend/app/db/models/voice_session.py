from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base import Base

class VoiceSessionStatus(str, enum.Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    ERROR = "ERROR"

class VoiceSession(Base):
    __tablename__ = "voice_sessions"

    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True, nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    input_duration = Column(Integer, default=0, comment="Duration of user input in milliseconds")
    output_duration = Column(Integer, default=0, comment="Duration of companion output in milliseconds")
    
    status = Column(String, default=VoiceSessionStatus.IDLE.value, nullable=False)
    provider = Column(String, nullable=True, comment="STT/TTS provider used, e.g., openai")
    error_code = Column(String, nullable=True)

    # Relationships (assuming models User, Companion, Conversation exist)
    # user = relationship("User")
    # companion = relationship("Companion")
    # conversation = relationship("Conversation")
