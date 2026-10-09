import time
from typing import Optional, List
from app.domain.awareness.awareness_context import SceneObjectType
from app.domain.shared_reality.shared_reality_context import (
    SharedRealityContext,
    JointAttentionState,
    CandidateFocus,
    AttentionAnchor,
    UserConfirmationStatus
)

class FocusPersistenceManager:
    """
    Manages temporal persistence (Focus Lock 3~10s), wrong focus recovery,
    and automatic 15-second inactivity timeout.
    """

    DEFAULT_LOCK_DURATION_MS: int = 6000 # 6 seconds
    TIMEOUT_DURATION_MS: int = 15000     # 15 seconds

    _current_context: Optional[SharedRealityContext] = None

    @classmethod
    def resolve_persistent_focus(
        cls,
        candidate: Optional[CandidateFocus],
        candidates: List[CandidateFocus],
        confirmation_status: UserConfirmationStatus,
        user_intent: str
    ) -> SharedRealityContext:
        now_ms = int(time.time() * 1000)

        # 1. Handle Inactivity Timeout
        if cls._current_context and cls._current_context.is_timed_out:
            cls._current_context = None

        # 2. Handle Wrong Focus Recovery (User rejects previous focus)
        if confirmation_status == UserConfirmationStatus.REJECTED:
            # Immediate unlock and exclude previous rejected target
            rejected_type = cls._current_context.focus_target if cls._current_context else None
            cls._current_context = None
            
            # Select alternative candidate if available
            alt_candidate = next((c for c in candidates if c.object_type != rejected_type), None)
            if alt_candidate and alt_candidate.confidence >= 0.70:
                new_ctx = SharedRealityContext(
                    state=JointAttentionState.SHARED_FOCUS,
                    focus_target=alt_candidate.object_type,
                    target_label=alt_candidate.label,
                    target_confidence=alt_candidate.confidence,
                    anchor=alt_candidate.anchor,
                    candidate_targets=candidates,
                    user_intent=f"Recovered focus after rejection: {alt_candidate.object_type.value}",
                    confirmation_status=UserConfirmationStatus.UNKNOWN,
                    shared_attention=True,
                    timestamp_ms=now_ms,
                    focus_lock_until_ms=now_ms + cls.DEFAULT_LOCK_DURATION_MS,
                    last_interaction_time_ms=now_ms
                )
                cls._current_context = new_ctx
                return new_ctx
            else:
                none_ctx = SharedRealityContext(
                    state=JointAttentionState.NONE,
                    anchor=AttentionAnchor.USER_FACE,
                    user_intent="Focus reset after rejection",
                    timestamp_ms=now_ms
                )
                cls._current_context = none_ctx
                return none_ctx

        # 3. If currently Locked and no explicit override, persist current focus
        if cls._current_context and cls._current_context.is_locked and cls._current_context.focus_target:
            cls._current_context.last_interaction_time_ms = now_ms
            cls._current_context.candidate_targets = candidates
            return cls._current_context

        # 4. New Focus Formation with Confidence Threshold (>= 0.75)
        if candidate and candidate.confidence >= SharedRealityContext.MIN_SHARED_FOCUS_CONFIDENCE:
            new_state = JointAttentionState.SHARED_FOCUS
            if confirmation_status == UserConfirmationStatus.CONFIRMED:
                new_state = JointAttentionState.DISCUSSING_TARGET

            new_ctx = SharedRealityContext(
                state=new_state,
                focus_target=candidate.object_type,
                target_label=candidate.label,
                target_confidence=candidate.confidence,
                anchor=candidate.anchor,
                candidate_targets=candidates,
                user_intent=user_intent,
                confirmation_status=confirmation_status,
                shared_attention=True,
                timestamp_ms=now_ms,
                focus_lock_until_ms=now_ms + cls.DEFAULT_LOCK_DURATION_MS,
                last_interaction_time_ms=now_ms
            )
            cls._current_context = new_ctx
            return new_ctx

        # 5. Low Confidence (0.45 ~ 0.74): User Focus only (No Joint Attention)
        if candidate and candidate.confidence >= 0.45:
            user_focus_ctx = SharedRealityContext(
                state=JointAttentionState.USER_FOCUS,
                focus_target=candidate.object_type,
                target_label=candidate.label,
                target_confidence=candidate.confidence,
                anchor=candidate.anchor,
                candidate_targets=candidates,
                user_intent=user_intent,
                shared_attention=False,
                timestamp_ms=now_ms,
                last_interaction_time_ms=now_ms
            )
            cls._current_context = user_focus_ctx
            return user_focus_ctx

        # 6. Fallback: NONE
        none_ctx = SharedRealityContext(
            state=JointAttentionState.NONE,
            anchor=AttentionAnchor.USER_FACE,
            timestamp_ms=now_ms
        )
        cls._current_context = none_ctx
        return none_ctx

    @classmethod
    def get_current_context(cls) -> Optional[SharedRealityContext]:
        if cls._current_context and cls._current_context.is_timed_out:
            cls._current_context = None
        return cls._current_context

    @classmethod
    def clear(cls) -> None:
        cls._current_context = None
