from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import time
from datetime import datetime

from app.domain.awareness.awareness_context import AwarenessContext
from app.domain.shared_reality.shared_reality_context import SharedRealityContext
from app.domain.adaptive.affective_state import UserAffectiveState
from app.domain.memory.relationship_memory import RelationshipMemory
from app.domain.proactive.proactive_context import ProactiveOpportunity

class TimeOfDay(str, Enum):
    MORNING = "MORNING"       # 06:00 ~ 11:59
    AFTERNOON = "AFTERNOON"   # 12:00 ~ 17:59
    EVENING = "EVENING"       # 18:00 ~ 22:59
    LATE_NIGHT = "LATE_NIGHT" # 23:00 ~ 05:59

class TemporalContext(BaseModel):
    time_of_day: TimeOfDay = TimeOfDay.AFTERNOON
    is_weekend: bool = False
    hour: int = 12
    formatted_time: str = ""

    @classmethod
    def current(cls) -> "TemporalContext":
        now = datetime.now()
        h = now.hour
        if 6 <= h < 12:
            tod = TimeOfDay.MORNING
        elif 12 <= h < 18:
            tod = TimeOfDay.AFTERNOON
        elif 18 <= h < 23:
            tod = TimeOfDay.EVENING
        else:
            tod = TimeOfDay.LATE_NIGHT

        is_wknd = now.weekday() >= 5
        return cls(
            time_of_day=tod,
            is_weekend=is_wknd,
            hour=h,
            formatted_time=now.strftime("%Y-%m-%d %H:%M")
        )

class CompanionCognitiveState(BaseModel):
    awareness_context: Optional[AwarenessContext] = None
    shared_reality_context: Optional[SharedRealityContext] = None
    affective_state: Optional[UserAffectiveState] = None
    recalled_memories: List[RelationshipMemory] = Field(default_factory=list)
    proactive_opportunity: Optional[ProactiveOpportunity] = None
    temporal_context: TemporalContext = Field(default_factory=TemporalContext.current)
    recent_assistant_intents: List[str] = Field(default_factory=list) # Meta-cognition history
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
