import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class UserCharacterPreference(Base):
    """
    Stores user's active character preference.
    Guarantees exactly one active character per user via UNIQUE(user_id).
    """
    __tablename__ = "user_character_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    active_companion_id = Column(String(50), ForeignKey("companions.id"), index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
    active_companion = relationship("Companion")
