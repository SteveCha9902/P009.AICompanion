from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
from app.domain.relationship.relationship_state import RelationshipStage

class LifeChapter(BaseModel):
    chapter_id: str
    user_id: str
    title: str                      # e.g. "아들 군 복무", "첫 식물 가꾸기"
    category: str                   # e.g. "FAMILY", "HOME", "CAREER"
    start_date_str: str = ""        # "YYYY-MM"
    end_date_str: str = ""          # "YYYY-MM" or empty if ongoing
    event_ids: List[str] = Field(default_factory=list) # Linked LifeEvent IDs
    summary_narrative: str = ""     # Continuous chapter story
    is_ongoing: bool = True
    created_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

class UserIdentitySnapshot(BaseModel):
    user_id: str
    core_interests: List[str] = Field(default_factory=list)
    life_stage: str = ""            # e.g. "학부모", "개발자", "식물 집사"
    observed_routines: List[str] = Field(default_factory=list)
    growth_notes: List[str] = Field(default_factory=list)
    last_updated_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

class RelationshipHistoryMilestone(BaseModel):
    milestone_id: str
    user_id: str
    stage: RelationshipStage
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    date_str: str = ""
    reflection_text: str = ""
    shared_memory_count: int = 0
