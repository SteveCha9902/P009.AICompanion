import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Text, UniqueConstraint
from app.db.base import Base


class CharacterGlobalGrowthModel(Base):
    """
    Global character growth states across the companion's entire life.
    """
    __tablename__ = "character_global_growth_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), unique=True, index=True, nullable=False, default="genie")
    support_style = Column(String(50), nullable=False, default="EMPATHIC_LISTENER")
    initiative_tendency = Column(String(50), nullable=False, default="BALANCED")
    global_learned_behavior = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRelationshipAdaptationModel(Base):
    """
    User-specific behavioral and communication adaptations.
    """
    __tablename__ = "user_relationship_adaptations"
    __table_args__ = (
        UniqueConstraint("user_id", "companion_id", name="uq_user_companion_adaptation"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="genie")
    preferred_formality = Column(Float, default=0.3, nullable=False)
    preferred_humor = Column(Float, default=0.6, nullable=False)
    preferred_directness = Column(Float, default=0.5, nullable=False)
    support_preference = Column(String(50), default="EMPATHIC_SUPPORT", nullable=False)
    conversation_rhythm = Column(String(50), default="NATURAL", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RelationshipMilestoneModel(Base):
    """
    Key milestones and shared turning points in a specific user-companion bond.
    """
    __tablename__ = "relationship_milestones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="genie")
    milestone_type = Column(String(50), nullable=False) # e.g. FIRST_DEEP_CONVERSATION, USER_CRISIS_SUPPORT
    significance = Column(Float, default=0.8, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
