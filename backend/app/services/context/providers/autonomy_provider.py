from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.services.autonomy.autonomy_engine import AutonomyEngine
from app.services.adaptive.affective_estimator import AffectiveStateEstimator
from app.services.adaptive.adaptive_behavior_planner import AdaptiveBehaviorPlanner
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator

class AutonomyContextProvider(ContextProvider):
    """
    Companion Autonomy Context Provider:
    Injects self-directed action choices and user comfort boundaries into ContextBuilder prompt.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        raw_aff = AffectiveStateEstimator.estimate_affective_state(current_user_message, awareness_ctx)
        planned_aff = AdaptiveBehaviorPlanner.plan_behavior(raw_aff)

        decision = AutonomyEngine.evaluate_autonomous_action(
            user_id=self.user_id,
            user_utterance=current_user_message,
            affective_state=planned_aff,
            awareness_context=awareness_ctx
        )

        return [{
            "role": "system",
            "content": (
                f"\n[COMPANION AUTONOMY AGENCY]\n"
                f"Selected Action: {decision.selected_action.value} (Confidence: {decision.confidence:.2f})\n"
                f"Rationale: {decision.user_facing_reason}\n"
                f"{decision.prompt_directive}"
            )
        }]
