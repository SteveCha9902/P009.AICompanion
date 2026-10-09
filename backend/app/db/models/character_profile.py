import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.db.base import Base

class CharacterProfileModel(Base):
    __tablename__ = "character_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False, default="지니")
    display_name = Column(String(50), nullable=False, default="Genie")
    age_appearance = Column(Integer, default=30)
    gender_expression = Column(String(20), default="female")
    origin_story = Column(Text, nullable=True)
    self_description = Column(Text, nullable=False)
    core_identity = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
