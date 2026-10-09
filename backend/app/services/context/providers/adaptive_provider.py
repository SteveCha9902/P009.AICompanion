from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.adaptive.affective_state import UserAffectiveState
from app.services.adaptive.affective_estimator import AffectiveStateEstimator
from app.services.adaptive.adaptive_behavior_planner import AdaptiveBehaviorPlanner
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator

class AdaptiveContextProvider(ContextProvider):
    """
    6th Cognitive Layer: Emotionally Adaptive Companion Provider.
    Injects dynamic empathy, tone modulation, and behavior directives into ContextBuilder prompt.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        raw_state = AffectiveStateEstimator.estimate_affective_state(
            user_utterance=current_user_message,
            awareness_context=awareness_ctx
        )
        planned_state = AdaptiveBehaviorPlanner.plan_behavior(raw_state)
        guidance = AdaptiveBehaviorPlanner.build_prompt_guidance(planned_state)

        if not guidance:
            return []
        return [{"role": "system", "content": guidance}]
