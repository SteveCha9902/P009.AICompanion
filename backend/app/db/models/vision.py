from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base import Base

class VisionSessionStatus(str, enum.Enum):
    CAMERA_OFF = "CAMERA_OFF"
    CAMERA_STARTING = "CAMERA_STARTING"
    CAMERA_ACTIVE = "CAMERA_ACTIVE"
    ANALYZING = "ANALYZING"
    VISION_READY = "VISION_READY"
    VISION_ERROR = "VISION_ERROR"

class VisionSession(Base):
    __tablename__ = "vision_sessions"

    id = Column(String, primary_key=True, index=True)
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default=VisionSessionStatus.CAMERA_OFF.value, nullable=False)

    observations = relationship("VisionObservation", back_populates="session", cascade="all, delete-orphan")


class VisionObservation(Base):
    __tablename__ = "vision_observations"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("vision_sessions.id"), index=True, nullable=False)
    
    observation_type = Column(String, index=True, nullable=False, comment="e.g. USER_DETECTED, FACE_DETECTED")
    confidence = Column(Float, nullable=False, default=1.0)
    data = Column(JSON, nullable=True, comment="Detailed JSON observation data")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("VisionSession", back_populates="observations")
