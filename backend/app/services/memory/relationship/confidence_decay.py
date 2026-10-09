import time
import math
from app.domain.memory.relationship_memory import RelationshipMemory

class ConfidenceDecayEngine:
    """
    Manages dynamic confidence modulation and temporal exponential decay.
    Confidence increases with direct & repeated references, and gradually decays over time.
    """

    DECAY_HALF_LIFE_DAYS = 90.0 # 90 days half-life

    @classmethod
    def update_on_reference(cls, memory: RelationshipMemory) -> None:
        now_ms = int(time.time() * 1000)
        memory.last_referenced_at_ms = now_ms
        memory.reference_count += 1
        # Confidence boost on repeated mention (capped at 0.99)
        memory.confidence = round(min(0.99, memory.confidence + 0.05), 2)


    @classmethod
    def calculate_effective_confidence(cls, memory: RelationshipMemory) -> float:
        """
        Applies exponential decay based on days since last reference.
        Pinned memories do not decay.
        """
        if memory.is_pinned:
            return memory.confidence

        now_ms = int(time.time() * 1000)
        days_passed = max(0.0, (now_ms - memory.last_referenced_at_ms) / (1000.0 * 60 * 60 * 24))
        decay_multiplier = math.exp(-0.693 * days_passed / cls.DECAY_HALF_LIFE_DAYS)
        return round(max(0.10, memory.confidence * decay_multiplier), 3)
