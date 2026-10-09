from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class TemporalContext(BaseModel):
    """
    Temporal awareness context capturing time of day, absence duration, and topic gaps.
    """
    current_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_of_day: str = "afternoon" # morning | afternoon | evening | night | late_night
    day_of_week: str = "Monday"
    last_interaction_at: Optional[datetime] = None
    absence_duration_hours: float = 0.0
    recent_activity_frequency: float = Field(default=0.5, ge=0.0, le=1.0)
    pending_topics: List[str] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        last_interaction_at: Optional[datetime] = None,
        now: Optional[datetime] = None,
        pending_topics: Optional[List[str]] = None
    ) -> "TemporalContext":
        current = now or datetime.now(timezone.utc)
        absence_hours = 0.0
        if last_interaction_at:
            delta = (current - last_interaction_at).total_seconds()
            absence_hours = max(0.0, delta / 3600.0)

        hour = current.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 22:
            time_of_day = "evening"
        elif 22 <= hour or hour < 2:
            time_of_day = "night"
        else:
            time_of_day = "late_night"

        return cls(
            current_time=current,
            time_of_day=time_of_day,
            day_of_week=current.strftime("%A"),
            last_interaction_at=last_interaction_at,
            absence_duration_hours=round(absence_hours, 2),
            pending_topics=pending_topics or []
        )
