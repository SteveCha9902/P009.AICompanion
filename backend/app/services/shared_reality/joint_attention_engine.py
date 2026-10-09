from typing import Optional, List
from app.domain.awareness.awareness_context import AwarenessContext
from app.domain.shared_reality.shared_reality_context import (
    SharedRealityContext,
    JointAttentionState
)
from app.services.shared_reality.user_intent_estimator import UserIntentEstimator
from app.services.shared_reality.focus_persistence_manager import FocusPersistenceManager

class JointAttentionEngine:
    """
    Synthesizes AwarenessContext (visual cues) and Conversation Utterance
    into a coherent SharedRealityContext with Joint Attention State Transitions.
    """

    @classmethod
    def evaluate_joint_attention(
        cls,
        user_utterance: str,
        awareness_context: Optional[AwarenessContext]
    ) -> SharedRealityContext:
        detected_objects = []
        if awareness_context and awareness_context.is_fresh:
            detected_objects = awareness_context.environment_state.detected_objects

        # 1. Estimate Focus and User Confirmation
        primary_cand, top_candidates, confirmation, intent_desc = UserIntentEstimator.estimate_focus_candidates(
            user_utterance=user_utterance,
            detected_objects=detected_objects
        )

        # 2. Resolve Temporal Persistence (Lock & Timeout & Recovery)
        shared_reality_ctx = FocusPersistenceManager.resolve_persistent_focus(
            candidate=primary_cand,
            candidates=top_candidates,
            confirmation_status=confirmation,
            user_intent=intent_desc
        )

        return shared_reality_ctx

    @classmethod
    def get_active_context(cls) -> Optional[SharedRealityContext]:
        return FocusPersistenceManager.get_current_context()

    @classmethod
    def reset(cls) -> None:
        FocusPersistenceManager.clear()
