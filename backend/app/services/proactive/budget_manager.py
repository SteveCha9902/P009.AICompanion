import time
from typing import Dict
from app.domain.proactive.proactive_context import ProactiveMode

class ProactiveBudgetManager:
    """
    Controls proactive conversation pacing and frequency budget:
    - NORMAL mode: Max 1 utterance per 30 minutes (1800s cooldown)
    - QUIET mode: Max 1~2 utterances per day (21600s cooldown = 6 hours)
    - OFF mode: Proactive disabled completely (0 utterances)
    """

    COOLDOWN_SECONDS_MAP: Dict[ProactiveMode, int] = {
        ProactiveMode.NORMAL: 1800,   # 30 minutes
        ProactiveMode.QUIET: 21600,   # 6 hours
        ProactiveMode.OFF: 999999999, # Disabled
    }

    _current_mode: ProactiveMode = ProactiveMode.NORMAL
    _last_proactive_time_ms: int = 0

    @classmethod
    def set_mode(cls, mode: ProactiveMode) -> None:
        cls._current_mode = mode

    @classmethod
    def get_mode(cls) -> ProactiveMode:
        return cls._current_mode

    @classmethod
    def can_initiate_proactive(cls) -> bool:
        if cls._current_mode == ProactiveMode.OFF:
            return False

        cooldown_sec = cls.COOLDOWN_SECONDS_MAP.get(cls._current_mode, 1800)
        now_ms = int(time.time() * 1000)
        elapsed_sec = (now_ms - cls._last_proactive_time_ms) / 1000.0
        return elapsed_sec >= cooldown_sec

    @classmethod
    def record_proactive_utterance(cls) -> None:
        cls._last_proactive_time_ms = int(time.time() * 1000)

    @classmethod
    def reset_cooldown(cls) -> None:
        cls._last_proactive_time_ms = 0
