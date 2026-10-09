from enum import Enum
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
import time

class TimelineCategory(str, Enum):
    # Auto-eligible Categories
    PET = "PET"
    HOBBY = "HOBBY"
    PROJECT = "PROJECT"
    GOAL = "GOAL"
    TRAVEL = "TRAVEL"
    HOME = "HOME"
    PREFERENCE = "PREFERENCE"

    # Consent-Required Sensitive Categories
    FAMILY = "FAMILY"
    HEALTH = "HEALTH"
    CAREER = "CAREER"
    FINANCIAL = "FINANCIAL"
    RELIGION = "RELIGION"
    POLITICS = "POLITICS"

class TimelinePrivacyPolicy:
    AUTO_ELIGIBLE: Set[TimelineCategory] = {
        TimelineCategory.PET,
        TimelineCategory.HOBBY,
        TimelineCategory.PROJECT,
        TimelineCategory.GOAL,
        TimelineCategory.TRAVEL,
        TimelineCategory.HOME,
        TimelineCategory.PREFERENCE
    }

    REQUIRES_CONSENT: Set[TimelineCategory] = {
        TimelineCategory.FAMILY,
        TimelineCategory.HEALTH,
        TimelineCategory.CAREER,
        TimelineCategory.FINANCIAL,
        TimelineCategory.RELIGION,
        TimelineCategory.POLITICS
    }

    @classmethod
    def is_eligible(cls, category: TimelineCategory, user_consented: bool = False) -> bool:
        if category in cls.AUTO_ELIGIBLE:
            return True
        return user_consented

class LifeEvent(BaseModel):
    event_id: str
    title: str
    category: TimelineCategory
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    event_date_str: str = "" # "YYYY-MM" or "YYYY-MM-DD"
    importance: float = Field(ge=0.0, le=1.0, default=0.8)
    confidence: float = Field(ge=0.0, le=1.0, default=0.85) # Event accuracy confidence
    related_memories: List[str] = Field(default_factory=list) # Memory IDs
    parent_event_id: Optional[str] = None # For causal linking (e.g. Plant purchase -> repotting)
    child_event_ids: List[str] = Field(default_factory=list)
    narrative_summary: str = ""

class LifeTimeline(BaseModel):
    user_id: str
    events: List[LifeEvent] = Field(default_factory=list)
    consented_categories: Set[TimelineCategory] = Field(default_factory=set)
    last_updated_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    def get_chronological_events(self, category: Optional[TimelineCategory] = None) -> List[LifeEvent]:
        evts = self.events
        if category:
            evts = [e for e in evts if e.category == category]
        return sorted(evts, key=lambda e: e.timestamp_ms)
