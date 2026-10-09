import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from app.db.base import Base

class CharacterBoundaryModel(Base):
    __tablename__ = "character_boundaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), index=True, nullable=False)
    topic = Column(String(100), nullable=False)
    response_policy = Column(String(100), nullable=False)
    flexibility = Column(Float, default=0.1, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
