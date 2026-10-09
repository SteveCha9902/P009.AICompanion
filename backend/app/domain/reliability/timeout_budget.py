import time
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TimeoutBudget(BaseModel):
    """
    Subsystem timeout budget configuration.
    """
    ttft_seconds: float = 15.0
    stream_idle_seconds: float = 30.0
    overall_request_seconds: float = 60.0
    db_query_seconds: float = 5.0
    tts_synthesis_seconds: float = 10.0
    vision_perception_seconds: float = 10.0
    memory_search_seconds: float = 5.0


class RateLimiter:
    """
    In-memory Token Bucket / Sliding Window Rate Limiter.
    Limits requests per key (user_id, IP, endpoint) to prevent cost spikes and abuse.
    """

    def __init__(self, max_requests_per_window: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests_per_window
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        timestamps = self._requests.get(key, [])
        # Purge timestamps older than window
        cutoff = now - self.window_seconds
        valid_timestamps = [t for t in timestamps if t > cutoff]

        if len(valid_timestamps) >= self.max_requests:
            self._requests[key] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self._requests[key] = valid_timestamps
        return True


class PrivacyRedactor:
    """
    Masks sensitive personal data, secrets, tokens, and credentials in logs and telemetry payloads.
    """
    SENSITIVE_KEYS = {
        "password", "secret", "token", "api_key", "access_token", "refresh_token",
        "authorization", "credentials", "credit_card"
    }

    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redacts sensitive fields in dictionaries."""
        redacted = {}
        for k, v in data.items():
            if any(sens in k.lower() for sens in cls.SENSITIVE_KEYS):
                redacted[k] = "[REDACTED]"
            elif isinstance(v, dict):
                redacted[k] = cls.redact_dict(v)
            elif isinstance(v, list):
                redacted[k] = [cls.redact_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                redacted[k] = v
        return redacted
