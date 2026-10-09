import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class CharacterPresentationProfileModel(Base):
    """
    DB entity storing character-specific presentation binding:
    Voice, Avatar, Expression, and Gesture profiles.
    """
    __tablename__ = "character_presentation_profiles"
    __table_args__ = (
        UniqueConstraint("companion_id", name="uq_character_presentation_profile"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), ForeignKey("companions.id"), index=True, nullable=False)
    
    voice_config = Column(JSON, nullable=False)
    avatar_config = Column(JSON, nullable=False)
    expression_config = Column(JSON, nullable=False)
    gesture_config = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
