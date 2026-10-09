from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.relationship.relationship_state import RelationshipStage
from app.services.relationship.relationship_growth_engine import RelationshipGrowthEngine
from app.services.adaptive.affective_estimator import AffectiveStateEstimator
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator

class RelationshipEvolutionContextProvider(ContextProvider):
    """
    Relationship Evolution Provider for ContextBuilder:
    Injects current RelationshipStage and appropriate intimacy/comfort guidance.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        raw_aff = AffectiveStateEstimator.estimate_affective_state(current_user_message, awareness_ctx)

        rel_state = RelationshipGrowthEngine.process_turn(
            user_id=self.user_id,
            user_utterance=current_user_message,
            affective_state=raw_aff,
            awareness_context=awareness_ctx
        )

        lines = [
            f"[RELATIONSHIP EVOLUTION STATE: {rel_state.stage.value}]",
            f"- Intimacy Metrics: Trust ({rel_state.vector.trust:.2f}), Familiarity ({rel_state.vector.familiarity:.2f}), Comfort ({rel_state.vector.comfort:.2f})."
        ]

        if rel_state.stage == RelationshipStage.STAGE_1_NEW:
            lines.append("- Guidance: Maintain respectful politeness, careful boundary observation, and gentle warmth.")
        elif rel_state.stage == RelationshipStage.STAGE_2_FAMILIAR:
            lines.append("- Guidance: Natural friendliness, moderate memory recall, and cozy conversation flow.")
        elif rel_state.stage == RelationshipStage.STAGE_3_TRUSTED:
            lines.append("- Guidance: Deeper emotional resonance, proactive interest in life projects, and warm security.")
        elif rel_state.stage == RelationshipStage.STAGE_4_DEEP:
            lines.append("- Guidance: Deep mutual understanding, comfortable silence, long-term journey partnership.")

        if rel_state.milestones:
            latest_ms = rel_state.milestones[-1]
            lines.append(f"- Recent Milestone: '{latest_ms.title}' ({latest_ms.event_date_str}).")

        return [{"role": "system", "content": "\n".join(lines)}]
