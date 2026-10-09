from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class RelationshipLevel(str, enum.Enum):
    STRANGER = "STRANGER"
    ACQUAINTANCE = "ACQUAINTANCE"
    FAMILIAR = "FAMILIAR"
    CLOSE = "CLOSE"
    TRUSTED = "TRUSTED"

class RelationshipSignalType(str, enum.Enum):
    USER_SHARED_SUCCESS = "USER_SHARED_SUCCESS"
    USER_SHARED_FAILURE = "USER_SHARED_FAILURE"
    USER_SHARED_PERSONAL_INFO = "USER_SHARED_PERSONAL_INFO"
    USER_ASKED_FOR_HELP = "USER_ASKED_FOR_HELP"
    USER_EXPRESSED_AFFECTION = "USER_EXPRESSED_AFFECTION"
    USER_EXPRESSED_TRUST = "USER_EXPRESSED_TRUST"
    USER_RETURNED = "USER_RETURNED"
    USER_RECALLED_MEMORY = "USER_RECALLED_MEMORY"
    USER_CORRECTED_COMPANION = "USER_CORRECTED_COMPANION"
    USER_REJECTED_COMPANION = "USER_REJECTED_COMPANION"
    COMPANION_HELPED_SUCCESSFULLY = "COMPANION_HELPED_SUCCESSFULLY"
    COMPANION_FAILED = "COMPANION_FAILED"
    COMPANION_REMEMBERED = "COMPANION_REMEMBERED"
    COMPANION_FORGOT = "COMPANION_FORGOT"
    USER_ADAPTATION_SUCCESS = "USER_ADAPTATION_SUCCESS"
    USER_ADAPTATION_FAILURE = "USER_ADAPTATION_FAILURE"

class SignalSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RelationshipState(Base):
    __tablename__ = "relationship_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), unique=True, index=True, nullable=False)
    user_id = Column(String, default="default_user", index=True, nullable=False)

    # 8-Dimensional Social Bond Model V2 (0.0 ~ 1.0)
    familiarity = Column(Float, nullable=False, default=0.1)
    trust = Column(Float, nullable=False, default=0.1)
    affection = Column(Float, nullable=False, default=0.1)
    intimacy = Column(Float, nullable=False, default=0.05)
    respect = Column(Float, nullable=False, default=0.3)
    comfort = Column(Float, nullable=False, default=0.1)
    attachment = Column(Float, nullable=False, default=0.05)
    playfulness = Column(Float, nullable=False, default=0.2)
    emotional_safety = Column(Float, nullable=False, default=0.2)
    shared_history_depth = Column(Float, nullable=False, default=0.0)

    # Legacy mappings (maintained for compatibility)
    closeness = Column(Float, nullable=False, default=0.1)
    engagement = Column(Float, nullable=False, default=0.5)
    reliability = Column(Float, nullable=False, default=0.5)


    # Stages & Presence
    stage = Column(String(50), nullable=False, default="stranger")
    relationship_level = Column(Enum(RelationshipLevel), nullable=False, default=RelationshipLevel.STRANGER)
    recent_presence = Column(Float, nullable=False, default=1.0)
    total_conversations = Column(Integer, nullable=False, default=0)
    last_interacted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    companion = relationship("Companion")

class RelationshipEvent(Base):
    __tablename__ = "relationship_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    
    signal_type = Column(String(100), nullable=False, default="GENERAL_INTERACTION")
    severity = Column(String(50), nullable=False, default="LOW")
    
    dimension_changed = Column(String, nullable=False) # e.g., "trust", "intimacy"
    delta_applied = Column(String, nullable=False)     # e.g., "+0.02"
    
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    companion = relationship("Companion")

class RelationshipAnchorModel(Base):
    """
    Immutable Social Anchors table.
    Persisted milestones across the companion's entire relationship lifetime.
    """
    __tablename__ = "relationship_anchors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    anchor_type = Column(String(50), nullable=False) # e.g. FIRST_MEETING, FIRST_PERSONAL_CONFESSION
    summary = Column(Text, nullable=False)
    importance = Column(Float, nullable=False, default=0.8)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

