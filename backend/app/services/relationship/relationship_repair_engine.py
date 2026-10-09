from app.domain.relationship.relationship_state import RelationshipState

class RelationshipRepairEngine:
    """
    Handles relationship strain and gradual trust repair.
    Provides empathetic recovery loops when misunderstandings or negative interactions occur.
    """

    @classmethod
    def apply_strain(cls, state: RelationshipState, severity: float = 0.15) -> RelationshipState:
        """
        Asymmetric drop: Trust falls faster than it grows.
        """
        state.vector.trust = max(0.10, state.vector.trust - severity)
        state.vector.comfort = max(0.10, state.vector.comfort - (severity * 0.8))
        state.stage = state.compute_stage()
        return state

    @classmethod
    def attempt_repair_step(cls, state: RelationshipState, positive_turn_quality: float) -> RelationshipState:
        """
        Gradual repair step when positive interactions resume.
        """
        if positive_turn_quality > 0.50:
            repair_inc = 0.03 * positive_turn_quality
            state.vector.trust = min(1.0, state.vector.trust + repair_inc)
            state.vector.comfort = min(1.0, state.vector.comfort + (repair_inc * 0.9))
            state.stage = state.compute_stage()
        return state
