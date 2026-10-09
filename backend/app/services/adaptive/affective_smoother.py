import time
from typing import Optional
from app.domain.adaptive.affective_state import UserAffectiveState

class AffectiveStateSmoother:
    """
    Applies Exponential Moving Average (EMA) smoothing over 5~10 second windows
    to eliminate rapid emotional jitter and provide steady, organic tone shifts.
    """

    ALPHA = 0.35 # Smoothing factor (0.35 gives responsive yet stable transition)
    _last_smoothed_state: Optional[UserAffectiveState] = None

    @classmethod
    def smooth_state(cls, raw_state: UserAffectiveState) -> UserAffectiveState:
        if cls._last_smoothed_state is None:
            cls._last_smoothed_state = raw_state
            return raw_state

        prev = cls._last_smoothed_state
        now_ms = int(time.time() * 1000)
        time_diff_sec = max(0.1, (now_ms - prev.timestamp_ms) / 1000.0)

        # If more than 30 seconds have passed, reset smoothing to raw state
        if time_diff_sec > 30.0:
            cls._last_smoothed_state = raw_state
            return raw_state

        smoothed_valence = round(cls.ALPHA * raw_state.emotional_valence + (1 - cls.ALPHA) * prev.emotional_valence, 3)
        smoothed_energy = round(cls.ALPHA * raw_state.energy_level + (1 - cls.ALPHA) * prev.energy_level, 3)
        smoothed_stress = round(cls.ALPHA * raw_state.stress_level + (1 - cls.ALPHA) * prev.stress_level, 3)
        smoothed_receptiveness = round(cls.ALPHA * raw_state.receptiveness + (1 - cls.ALPHA) * prev.receptiveness, 3)
        smoothed_conf = round(cls.ALPHA * raw_state.confidence + (1 - cls.ALPHA) * prev.confidence, 3)

        smoothed_state = UserAffectiveState(
            emotional_valence=smoothed_valence,
            energy_level=smoothed_energy,
            stress_level=smoothed_stress,
            receptiveness=smoothed_receptiveness,
            confidence=smoothed_conf,
            adaptive_mode=raw_state.adaptive_mode,
            voice_params=raw_state.voice_params,
            timestamp_ms=now_ms
        )

        cls._last_smoothed_state = smoothed_state
        return smoothed_state

    @classmethod
    def reset(cls) -> None:
        cls._last_smoothed_state = None
