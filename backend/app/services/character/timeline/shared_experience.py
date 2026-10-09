from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SharedExperience(BaseModel):
    """
    Represents an episodic narrative milestone shared between a user and the companion.
    Distinct from standard declarative fact memory.
    """
    experience_id: str
    user_id: str
    companion_id: str
    event_type: str
    importance: float = Field(default=0.8, ge=0.0, le=1.0)
    summary: str
    emotional_significance: str # e.g. "deep_support", "joyful_breakthrough"
    relationship_impact: float = 0.05
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SharedExperienceEngine:
    """
    Manages and retrieves shared experience narrative chains.
    """

    @staticmethod
    def create_experience_from_milestone(
        experience_id: str,
        user_id: str,
        companion_id: str,
        event_type: str,
        summary: str,
        importance: float = 0.85
    ) -> SharedExperience:
        significance = "meaningful_shared_moment"
        if "CRISIS" in event_type or "SECRET" in event_type:
            significance = "deep_support_and_vulnerability"
        elif "ACHIEVEMENT" in event_type:
            significance = "celebratory_milestone"

        return SharedExperience(
            experience_id=experience_id,
            user_id=user_id,
            companion_id=companion_id,
            event_type=event_type,
            importance=importance,
            summary=summary,
            emotional_significance=significance,
            relationship_impact=round(importance * 0.1, 3)
        )
