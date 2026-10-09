from typing import Optional, Dict, List
import time
from app.domain.timeline.life_event import LifeTimeline, LifeEvent, TimelineCategory, TimelinePrivacyPolicy
from app.domain.memory.relationship_memory import RelationshipMemory, MemoryType

class TimelineBuilder:
    """
    Constructs and maintains LifeTimelines while strictly enforcing Privacy & Consent Policies.
    """

    _timelines: Dict[str, LifeTimeline] = {}

    @classmethod
    def get_or_create_timeline(cls, user_id: str) -> LifeTimeline:
        if user_id not in cls._timelines:
            cls._timelines[user_id] = LifeTimeline(user_id=user_id)
        return cls._timelines[user_id]

    @classmethod
    def register_event(
        cls,
        user_id: str,
        title: str,
        category: TimelineCategory,
        event_date_str: str = "",
        importance: float = 0.80,
        confidence: float = 0.85,
        related_memories: Optional[List[str]] = None,
        parent_event_id: Optional[str] = None
    ) -> Optional[LifeEvent]:
        timeline = cls.get_or_create_timeline(user_id)

        # Check Privacy Policy & Consent
        user_consented = category in timeline.consented_categories
        if not TimelinePrivacyPolicy.is_eligible(category, user_consented):
            # Block sensitive event registration if user hasn't explicitly consented
            return None

        event = LifeEvent(
            event_id=f"evt_{int(time.time() * 1000)}_{len(timeline.events)}",
            title=title,
            category=category,
            event_date_str=event_date_str or time.strftime("%Y-%m"),
            importance=importance,
            confidence=confidence,
            related_memories=related_memories or [],
            parent_event_id=parent_event_id
        )

        timeline.events.append(event)
        if parent_event_id:
            parent = next((e for e in timeline.events if e.event_id == parent_event_id), None)
            if parent and event.event_id not in parent.child_event_ids:
                parent.child_event_ids.append(event.event_id)

        timeline.last_updated_ms = int(time.time() * 1000)
        return event

    @classmethod
    def grant_consent(cls, user_id: str, category: TimelineCategory) -> None:
        timeline = cls.get_or_create_timeline(user_id)
        timeline.consented_categories.add(category)

    @classmethod
    def clear(cls) -> None:
        cls._timelines.clear()
