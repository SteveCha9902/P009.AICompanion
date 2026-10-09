from typing import List, Optional
from pydantic import BaseModel, Field
from app.domain.memory.story_chapter import StoryChapter
from app.domain.memory.shared_experience import SharedExperience
from app.domain.memory.life_event import LifeEvent

class AutobiographicalContext(BaseModel):
    active_chapters: List[StoryChapter] = Field(default_factory=list)
    shared_experiences: List[SharedExperience] = Field(default_factory=list)
    recent_life_events: List[LifeEvent] = Field(default_factory=list)
    narrative_summary: Optional[str] = None
