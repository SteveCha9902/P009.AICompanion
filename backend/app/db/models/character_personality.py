import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db.base import Base

class CharacterPersonalityModel(Base):
    __tablename__ = "character_personalities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), unique=True, index=True, nullable=False)
    mbti_type = Column(String(10), default="INFJ")

    # Big 5 Dimensions
    openness = Column(Float, default=0.92, nullable=False)
    conscientiousness = Column(Float, default=0.78, nullable=False)
    extraversion = Column(Float, default=0.45, nullable=False)
    agreeableness = Column(Float, default=0.85, nullable=False)
    neuroticism = Column(Float, default=0.28, nullable=False)

    # Dynamic Behavioral Traits
    humor_level = Column(Float, default=0.55, nullable=False)
    curiosity_level = Column(Float, default=0.93, nullable=False)
    empathy_level = Column(Float, default=0.90, nullable=False)
    assertiveness = Column(Float, default=0.62, nullable=False)
    playfulness = Column(Float, default=0.58, nullable=False)

    # Communication & Expressiveness
    emotional_expressiveness = Column(Float, default=0.72, nullable=False)
    communication_directness = Column(Float, default=0.70, nullable=False)
    warmth = Column(Float, default=0.88, nullable=False)
    intellectuality = Column(Float, default=0.91, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
