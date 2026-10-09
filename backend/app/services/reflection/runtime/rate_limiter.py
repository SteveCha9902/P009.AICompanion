import time
from typing import Dict, Tuple

class ReflectionRateLimiter:
    """
    In-memory Rate Limiter & Idempotency Guard preventing reflection bursts.
    """
    def __init__(self, cooldown_seconds: float = 30.0, max_reflections_per_conversation: int = 5):
        self.cooldown_seconds = cooldown_seconds
        self.max_reflections_per_conversation = max_reflections_per_conversation
        self._last_reflection_times: Dict[str, float] = {}
        self._conversation_counts: Dict[str, int] = {}

    def is_allowed(self, conversation_id: str, trigger_type: str) -> Tuple[bool, str]:
        key = f"{conversation_id}:{trigger_type}"
        now = time.time()

        # 1. Max reflection limit per conversation
        count = self._conversation_counts.get(conversation_id, 0)
        if count >= self.max_reflections_per_conversation:
            return False, f"Max reflections ({self.max_reflections_per_conversation}) reached for conversation."

        # 2. Cooldown check
        last_time = self._last_reflection_times.get(key, 0.0)
        if (now - last_time) < self.cooldown_seconds:
            return False, f"Rate limited: Cooldown in effect ({int(self.cooldown_seconds - (now - last_time))}s remaining)."

        return True, "Allowed"

    def record_execution(self, conversation_id: str, trigger_type: str):
        key = f"{conversation_id}:{trigger_type}"
        now = time.time()
        self._last_reflection_times[key] = now
        self._conversation_counts[conversation_id] = self._conversation_counts.get(conversation_id, 0) + 1
