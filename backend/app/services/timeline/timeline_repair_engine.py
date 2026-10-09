from typing import Optional
from app.domain.timeline.life_event import LifeTimeline, LifeEvent, TimelineCategory

class TimelineRepairEngine:
    """
    Handles user corrections when memories or timeline details were inaccurate or misremembered.
    (e.g., 'No, it wasn't a plant, it was a ceramic flower pot.')
    """

    @classmethod
    def repair_event_title(cls, timeline: LifeTimeline, event_id: str, new_title: str) -> Optional[LifeEvent]:
        for e in timeline.events:
            if e.event_id == event_id:
                e.title = new_title
                e.confidence = 1.0 # User explicitly confirmed
                return e
        return None

    @classmethod
    def correct_event_category(cls, timeline: LifeTimeline, event_id: str, new_category: TimelineCategory) -> Optional[LifeEvent]:
        for e in timeline.events:
            if e.event_id == event_id:
                e.category = new_category
                return e
        return None

    @classmethod
    def remove_inaccurate_event(cls, timeline: LifeTimeline, event_id: str) -> bool:
        initial_len = len(timeline.events)
        timeline.events = [e for e in timeline.events if e.event_id != event_id]
        return len(timeline.events) < initial_len
