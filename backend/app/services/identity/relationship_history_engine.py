from typing import Dict, List, Optional
import time
from app.domain.identity.identity_state import RelationshipHistoryMilestone
from app.domain.relationship.relationship_state import RelationshipStage

class RelationshipHistoryEngine:
    """
    Chronicles the multi-month/multi-year bond progression between user and companion.
    """

    _history: Dict[str, List[RelationshipHistoryMilestone]] = {}

    @classmethod
    def record_stage_transition(
        cls,
        user_id: str,
        stage: RelationshipStage,
        date_str: str,
        reflection_text: str,
        shared_memory_count: int = 0
    ) -> RelationshipHistoryMilestone:
        if user_id not in cls._history:
            cls._history[user_id] = []

        m = RelationshipHistoryMilestone(
            milestone_id=f"rel_m_{int(time.time()*1000)}",
            user_id=user_id,
            stage=stage,
            date_str=date_str,
            reflection_text=reflection_text,
            shared_memory_count=shared_memory_count
        )
        cls._history[user_id].append(m)
        return m

    @classmethod
    def list_history(cls, user_id: str) -> List[RelationshipHistoryMilestone]:
        return cls._history.get(user_id, [])

    @classmethod
    def clear(cls) -> None:
        cls._history.clear()
