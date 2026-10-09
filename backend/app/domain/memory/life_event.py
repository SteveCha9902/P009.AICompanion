import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class LifeEventCategory(str, Enum):
    PROJECT_MILESTONE = "PROJECT_MILESTONE"
    PERSONAL_MILESTONE = "PERSONAL_MILESTONE"
    FAMILY_EVENT = "FAMILY_EVENT"
    CAREER_EVENT = "CAREER_EVENT"
    TRAVEL_EVENT = "TRAVEL_EVENT"
    CREATIVE_EVENT = "CREATIVE_EVENT"
    DIFFICULT_PERIOD = "DIFFICULT_PERIOD"
    ACHIEVEMENT = "ACHIEVEMENT"
    IMPORTANT_DECISION = "IMPORTANT_DECISION"
    SHARED_CONVERSATION = "SHARED_CONVERSATION"
    RELATIONSHIP_MILESTONE = "RELATIONSHIP_MILESTONE"

class LifeEvent(BaseModel):
    """
    High-significance Life Event promoted from Episodic Memories.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    companion_id: str = "default_companion"
    title: str
    summary: str
    category: LifeEventCategory = LifeEventCategory.PROJECT_MILESTONE
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    importance: float = Field(default=0.8, ge=0.0, le=1.0)
    emotional_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    relationship_significance: float = Field(default=0.7, ge=0.0, le=1.0)
    source_episode_ids: List[str] = Field(default_factory=list)
