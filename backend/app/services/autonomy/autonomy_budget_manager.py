from typing import List, Dict
import time

class AutonomyBudgetManager:
    """
    Manages autonomous speech quota to prevent over-talkative AI.
    Rules: Max 1 proactive utterance per 15 minutes, Max 3 per hour.
    Throttles budget if user provides consecutive single-syllable responses.
    """

    _speech_timestamps: List[int] = []
    _consecutive_unresponsive_turns: int = 0

    @classmethod
    def can_initiate_autonomous_speech(cls) -> bool:
        now_ms = int(time.time() * 1000)

        # 1. User responsiveness throttle
        if cls._consecutive_unresponsive_turns >= 2:
            return False

        # 2. 15-minute window check (max 1)
        fifteen_min_ago = now_ms - (15 * 60 * 1000)
        recent_15m = [t for t in cls._speech_timestamps if t >= fifteen_min_ago]
        if len(recent_15m) >= 1:
            return False

        # 3. 1-hour window check (max 3)
        one_hour_ago = now_ms - (60 * 60 * 1000)
        recent_1h = [t for t in cls._speech_timestamps if t >= one_hour_ago]
        if len(recent_1h) >= 3:
            return False

        return True

    @classmethod
    def record_autonomous_speech(cls) -> None:
        cls._speech_timestamps.append(int(time.time() * 1000))
        if len(cls._speech_timestamps) > 20:
            cls._speech_timestamps.pop(0)

    @classmethod
    def record_user_responsiveness(cls, is_responsive: bool) -> None:
        if is_responsive:
            cls._consecutive_unresponsive_turns = 0
        else:
            cls._consecutive_unresponsive_turns += 1

    @classmethod
    def clear(cls) -> None:
        cls._speech_timestamps.clear()
        cls._consecutive_unresponsive_turns = 0
