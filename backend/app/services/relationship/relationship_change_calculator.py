from typing import List, Dict
from datetime import datetime
from app.domain.relationship.relationship_dimensions import RelationshipDimensions
from app.domain.relationship.relationship_event import RelationshipEventType

MAX_DELTA_PER_INTERACTION = 0.03

class RelationshipChangeCalculator:
    """
    Calculates incremental deltas across 7 relationship dimensions with strict rate limiting.
    """

    @staticmethod
    def calculate_deltas(
        events: List[RelationshipEventType],
        current_dimensions: RelationshipDimensions
    ) -> Dict[str, float]:
        deltas: Dict[str, float] = {
            "familiarity": 0.0,
            "trust": 0.0,
            "affection": 0.0,
            "intimacy": 0.0,
            "respect": 0.0,
            "comfort": 0.0,
            "attachment": 0.0
        }

        # 1. Base familiarity increment on every conversation
        deltas["familiarity"] += 0.005
        deltas["comfort"] += 0.003

        # 2. Event-specific deltas
        for ev in events:
            if ev == RelationshipEventType.FIRST_CONVERSATION:
                deltas["familiarity"] += 0.02
                deltas["respect"] += 0.02
            elif ev == RelationshipEventType.PERSONAL_STORY_SHARED:
                deltas["intimacy"] += 0.025
                deltas["trust"] += 0.02
                deltas["comfort"] += 0.015
            elif ev == RelationshipEventType.USER_SHOWED_TRUST:
                deltas["trust"] += 0.025
                deltas["comfort"] += 0.01
            elif ev == RelationshipEventType.USER_REQUESTED_ADVICE:
                deltas["trust"] += 0.015
                deltas["respect"] += 0.01
            elif ev == RelationshipEventType.USER_EXPRESSED_GRATITUDE:
                deltas["affection"] += 0.02
                deltas["comfort"] += 0.01
            elif ev == RelationshipEventType.USER_EXPRESSED_AFFECTION:
                deltas["affection"] += 0.025
                deltas["attachment"] += 0.015
            elif ev == RelationshipEventType.RETURN_AFTER_ABSENCE:
                deltas["affection"] += 0.01
                deltas["comfort"] += 0.01

        # 3. Apply Strict Rate Limit Guard (Max delta per interaction <= 0.03)
        for dim in deltas:
            deltas[dim] = max(-MAX_DELTA_PER_INTERACTION, min(MAX_DELTA_PER_INTERACTION, round(deltas[dim], 4)))

        return deltas

    @staticmethod
    def apply_decay(
        dimensions: RelationshipDimensions,
        days_absent: float
    ) -> Dict[str, float]:
        """
        Hierarchical Decay:
        - Recent Presence: Fast Decay (handled in state)
        - Familiarity & Comfort: Very Slow Decay
        - Trust & Respect: Almost Invariant (Preserved Core)
        """
        if days_absent < 7.0:
            return {}

        decay_factor = min(0.05, (days_absent - 7.0) * 0.001)
        return {
            "familiarity": -decay_factor * 0.5,
            "comfort": -decay_factor * 0.5,
            "attachment": -decay_factor * 0.8,
            "trust": -decay_factor * 0.1,  # Trust barely decays
            "respect": 0.0,
            "intimacy": 0.0,
            "affection": -decay_factor * 0.2
        }
