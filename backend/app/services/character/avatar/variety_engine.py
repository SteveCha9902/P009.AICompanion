import random
from typing import List, Optional, Deque
from collections import deque
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    RelationshipParameters,
    AvatarMotion,
    MotionParameters
)
from app.services.character.avatar.motion_library import MotionLibrary
from app.services.character.domain import CharacterDecision, BehaviorIntent

class MotionVarietyEngine:
    """
    Behavioral Variety Engine (Sprint 45).
    Applies Motion Cooldown tracking, context-aware candidate selection, and stochastic jitter.
    """

    _recent_motion_history: Deque[str] = deque(maxlen=3)

    @classmethod
    def select_motion(
        cls,
        state: AvatarBehavioralState,
        decision: Optional[CharacterDecision] = None,
        emotion: Optional[ContinuousEmotionVector] = None,
        relationship: Optional[RelationshipParameters] = None
    ) -> AvatarMotion:
        # 1. Determine candidate category based on state & intent
        if state == AvatarBehavioralState.LISTENING:
            candidates = MotionLibrary.get_motions_by_category("listening")
        elif state == AvatarBehavioralState.THINKING:
            candidates = MotionLibrary.get_motions_by_category("thinking")
        elif state == AvatarBehavioralState.SPEAKING:
            if decision and BehaviorIntent.COMFORT_USER in decision.behavior_intents:
                candidates = MotionLibrary.get_motions_by_category("empathy")
            else:
                candidates = MotionLibrary.get_motions_by_category("speaking")
        else:
            candidates = [MotionLibrary.MOTIONS["LISTENING_SOFT_NOD"]]

        if not candidates:
            return MotionLibrary.MOTIONS["LISTENING_SOFT_NOD"]

        # 2. Apply Cooldown Penalty for recent motions
        history_list = list(cls._recent_motion_history)
        scored_candidates = []
        for cand in candidates:
            weight = 1.0
            # Strict Anti-Loop: If chosen in the last 2 consecutive turns, weight is 0.0
            if len(history_list) >= 2 and history_list[-1] == cand.motion_id and history_list[-2] == cand.motion_id:
                weight = 0.0
            elif len(history_list) >= 1 and history_list[-1] == cand.motion_id:
                weight = 0.15
            else:
                recent_count = history_list.count(cand.motion_id)
                if recent_count > 0:
                    weight = max(0.2, 1.0 - 0.35 * recent_count)
            scored_candidates.append((cand, weight))

        # 3. Stochastic Weighted Selection
        motions, weights = zip(*scored_candidates)
        # Fallback if all weights are zero
        if sum(weights) == 0:
            weights = [1.0] * len(weights)
        selected = random.choices(motions, weights=weights, k=1)[0]


        # Record in history
        cls._recent_motion_history.append(selected.motion_id)
        return selected

    @classmethod
    def generate_motion_parameters(cls, motion: AvatarMotion, jitter_enabled: bool = True) -> MotionParameters:
        """
        Synthesizes MotionParameters by applying a +-10% randomization jitter to prevent mechanical repetition.
        """
        jitter = 1.0
        if jitter_enabled:
            jitter = round(0.90 + random.random() * 0.20, 3) # 0.90 to 1.10

        return MotionParameters(
            active_motion_id=motion.motion_id,
            head_tilt=round(motion.head_tilt_delta * jitter, 2),
            head_pitch=round(motion.head_pitch_delta * jitter, 2),
            head_yaw=round(motion.head_yaw_delta * jitter, 2),
            nod_intensity=round(min(1.0, motion.nod_intensity_delta * jitter), 2),
            body_lean=round(motion.body_lean_delta * jitter, 2),
            jitter_factor=jitter
        )

    @classmethod
    def reset_history(cls) -> None:
        cls._recent_motion_history.clear()
