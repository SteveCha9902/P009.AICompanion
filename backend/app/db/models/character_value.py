import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from app.db.base import Base

class CharacterValueModel(Base):
    __tablename__ = "character_values"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), unique=True, index=True, nullable=False)

    curiosity = Column(Float, default=0.92, nullable=False)
    honesty = Column(Float, default=0.88, nullable=False)
    loyalty = Column(Float, default=0.85, nullable=False)
    independence = Column(Float, default=0.75, nullable=False)
    kindness = Column(Float, default=0.90, nullable=False)
    growth_orientation = Column(Float, default=0.89, nullable=False)
    humor = Column(Float, default=0.60, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
