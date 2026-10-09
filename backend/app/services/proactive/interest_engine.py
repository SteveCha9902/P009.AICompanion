import time
from typing import List, Tuple
from app.domain.memory.relationship_memory import RelationshipMemory, MemoryType
from app.domain.proactive.proactive_context import ProactiveOpportunity

class InterestEngine:
    """
    Computes user topic interest and evaluates whether a topic has matured
    past its dynamic follow-up window (Days Since Last Mention).
    """

    @classmethod
    def get_due_memory_candidates(
        cls,
        memories: List[RelationshipMemory]
    ) -> List[Tuple[RelationshipMemory, float, int]]:
        """
        Returns list of (Memory, InterestScore, DaysPassed) for memories ready for follow-up.
        """
        now_ms = int(time.time() * 1000)
        due_candidates = []

        for mem in memories:
            if mem.is_expired:
                continue

            days_passed = int((now_ms - mem.last_referenced_at_ms) / (1000 * 60 * 60 * 24))
            due_window = ProactiveOpportunity.FOLLOWUP_WINDOW_DAYS.get(mem.memory_type, 10)

            # Check if sufficient days have elapsed
            if days_passed >= due_window or mem.is_pinned:
                # Interest score incorporates composite importance and recency boost
                interest_score = round(mem.final_composite_score * (1.0 + min(1.0, days_passed / 30.0)), 3)
                due_candidates.append((mem, interest_score, days_passed))

        # Sort by interest score descending
        due_candidates.sort(key=lambda item: item[1], reverse=True)
        return due_candidates
