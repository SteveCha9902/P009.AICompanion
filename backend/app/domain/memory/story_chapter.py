import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class StoryChapter(BaseModel):
    """
    Narrative Chapter grouping significant milestones into an overarching life theme.
    (e.g., 'Chapter 1: The Beginning', 'Chapter 2: The Shared Project')
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    companion_id: str = "default_companion"
    chapter_number: int = 1
    title: str
    theme: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    summary: str
    importance: float = Field(default=0.9, ge=0.0, le=1.0)
    event_ids: List[str] = Field(default_factory=list)
