from app.domain.relationship.relationship_state import RelationshipVector

class TrustCalculator:
    """
    Computes trust progression independently from interaction familiarity.
    Trust requires consistency, emotional resonance, and reliable support over time.
    """

    @classmethod
    def calculate_trust_increment(
        cls,
        current_vector: RelationshipVector,
        turn_quality: float,
        memories_count: int,
        is_repair_mode: bool = False
    ) -> float:
        # High quality turn yields small gradual trust increment
        base_inc = (turn_quality - 0.35) * 0.015

        # Memory depth bonus
        if memories_count >= 5:
            base_inc += 0.005

        if is_repair_mode:
            # During repair, trust rebuilds at slightly reduced rate to ensure authenticity
            base_inc *= 0.70

        return max(-0.05, min(0.02, base_inc))
