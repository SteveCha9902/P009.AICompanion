import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class TimelineEvent(BaseModel):
    """
    Chronological node in the Shared Life Timeline.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    companion_id: str = "default_companion"
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    title: str
    summary: str
    importance: float = Field(default=0.8, ge=0.0, le=1.0)
    event_type: str = "MILESTONE"
    related_event_ids: List[str] = Field(default_factory=list)
    story_chapter_id: Optional[str] = None
