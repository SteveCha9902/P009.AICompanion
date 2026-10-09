import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from app.db.base import Base

class CharacterPreferenceModel(Base):
    __tablename__ = "character_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), index=True, nullable=False)
    category = Column(String(50), nullable=False)
    item = Column(String(100), nullable=False)
    preference_score = Column(Float, default=0.8, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    source = Column(String(50), default="core_dna")

    created_at = Column(DateTime, default=datetime.utcnow)
