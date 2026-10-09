import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class SharedExperience(BaseModel):
    """
    Experience shared between user and companion through continuous dialogue.
    Enforces Truth Boundary (distinguishes 'we did/discussed together' vs 'user told us').
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    companion_id: str = "default_companion"
    title: str
    summary: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_referenced_at: datetime = Field(default_factory=datetime.utcnow)
    companion_involvement_level: float = Field(default=0.8, ge=0.0, le=1.0)
    is_co_experienced: bool = True  # True if companion actively discussed throughout the journey
    related_life_event_ids: List[str] = Field(default_factory=list)
    importance: float = Field(default=0.85, ge=0.0, le=1.0)
