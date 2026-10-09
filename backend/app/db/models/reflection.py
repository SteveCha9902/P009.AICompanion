import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from app.db.base import Base

class ReflectionRecordModel(Base):
    __tablename__ = "reflection_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    conversation_id = Column(String(50), index=True, nullable=False, default="default")
    interaction_id = Column(String(50), nullable=True)
    trigger_type = Column(String(50), nullable=False)
    priority = Column(String(20), default="NORMAL", nullable=False)
    importance_score = Column(Float, default=0.5, nullable=False)
    reflection_summary = Column(Text, default="", nullable=False)
    emotional_pattern = Column(JSON, default=dict)
    relationship_insight = Column(JSON, default=dict)
    behavioral_hints = Column(JSON, default=list)
    status = Column(String(20), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
