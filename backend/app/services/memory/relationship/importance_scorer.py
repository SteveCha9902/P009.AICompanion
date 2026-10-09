from typing import Tuple
from app.domain.memory.relationship_memory import MemoryType

class ImportanceScoringEngine:
    """
    Evaluates memories using a 3-Axis Scoring Matrix:
    1. Importance (Core life relevance: 0.0 ~ 1.0)
    2. Future Relevance (Will this matter next week/month?: 0.0 ~ 1.0)
    3. Relationship Value (Does remembering this build emotional bond?: 0.0 ~ 1.0)
    """

    # Baseline weights by Memory Type
    TYPE_WEIGHTS = {
        MemoryType.PET: (0.95, 0.95, 0.95),        # High bond, lifelong
        MemoryType.PERSON: (0.90, 0.90, 0.95),     # Family, close friends
        MemoryType.GOAL: (0.90, 0.85, 0.80),       # Life goals, fitness, career
        MemoryType.PROJECT: (0.85, 0.80, 0.75),    # Long-term work/project
        MemoryType.HOBBY: (0.80, 0.75, 0.80),      # Personal passions
        MemoryType.PREFERENCE: (0.75, 0.70, 0.75), # Coffee preference, dislikes
        MemoryType.PLACE: (0.70, 0.65, 0.65),      # Travel, favorite cafe
        MemoryType.OBJECT: (0.65, 0.50, 0.60),     # Meaningful gifts, plants, mugs
        MemoryType.EVENT: (0.50, 0.30, 0.40),      # One-off meetings, dinners
    }

    # Minimum composite threshold required for persistence (0.15 ~= 0.60 avg across 3 axes)
    MIN_COMPOSITE_THRESHOLD = 0.15

    @classmethod
    def evaluate_3_axis_scores(
        cls,
        memory_type: MemoryType,
        summary: str,
        is_routine_event: bool = False
    ) -> Tuple[float, float, float, float]:
        """
        Returns (importance_score, future_relevance, relationship_value, composite_score)
        """
        imp, fut, rel = cls.TYPE_WEIGHTS.get(memory_type, (0.5, 0.5, 0.5))

        # Routine transient events (e.g. "오늘 저녁 회식이야", "점심에 김치찌개 먹었어")
        if is_routine_event or "회식" in summary or "점심" in summary or "오늘 저녁" in summary:
            imp = min(imp, 0.20)
            fut = min(fut, 0.10)
            rel = min(rel, 0.15)

        composite = round(imp * fut * rel, 3)
        return (imp, fut, rel, composite)

    @classmethod
    def should_persist(cls, composite_score: float) -> bool:
        return composite_score >= cls.MIN_COMPOSITE_THRESHOLD
