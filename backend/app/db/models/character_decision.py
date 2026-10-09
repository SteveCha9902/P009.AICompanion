import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from app.db.base import Base

class CharacterDecisionModel(Base):
    __tablename__ = "character_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id = Column(String(50), index=True, nullable=False)
    character_id = Column(String(50), index=True, nullable=False, default="genie")
    situation_type = Column(String(50), nullable=False, default="GENERAL_CONVERSATION")
    response_style = Column(String(50), nullable=False, default="WARM_SUPPORTIVE")
    behavior_intents = Column(JSON, default=list)
    emotional_intensity = Column(Float, default=0.5, nullable=False)
    initiative_level = Column(Float, default=0.5, nullable=False)
    humor_probability = Column(Float, default=0.3, nullable=False)
    decision_confidence = Column(Float, default=0.85, nullable=False)
    validation_score = Column(Float, default=1.0, nullable=False)
    validation_result = Column(String(20), default="PASS", nullable=False)
    validation_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
