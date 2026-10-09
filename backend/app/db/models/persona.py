from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Persona(Base):
    __tablename__ = "personas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False, unique=True)
    name = Column(String, nullable=False)
    
    # Core Persona traits
    personality = Column(JSON, default=dict) # e.g. {"warm": 80, "direct": 30}
    communication_style = Column(JSON, default=dict) # e.g. {"tone": "friendly", "verbosity": "medium"}
    values = Column(JSON, default=dict) # Key beliefs
    behavior_rules = Column(JSON, default=list) # List of strings
    boundaries = Column(JSON, default=list) # List of strings

    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    companion = relationship("Companion", back_populates="persona")
