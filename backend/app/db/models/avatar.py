from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class AvatarProfile(Base):
    __tablename__ = "avatar_profiles"

    id = Column(String, primary_key=True, index=True)
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False, unique=True)
    
    avatar_type = Column(String, default="2d_character", nullable=False)
    visual_style = Column(String, default="anime", nullable=False)
    default_expression = Column(String, default="neutral", nullable=False)
    default_motion = Column(String, default="idle", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to companion (assuming Companion model exists)
    # companion = relationship("Companion", back_populates="avatar_profile")
