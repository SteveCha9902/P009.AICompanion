from typing import Dict, Set
import time

class MemorySuppressionEngine:
    """
    Prevents repetitive mention of the same memory or topic within 7 days.
    Suppresses memories that user previously showed disinterest in.
    """

    _recently_recalled_topics: Dict[str, int] = {} # topic -> timestamp_ms
    _disinterested_topics: Set[str] = set()

    SUPPRESSION_WINDOW_MS = 7 * 24 * 3600 * 1000 # 7 days

    @classmethod
    def is_suppressed(cls, topic: str) -> bool:
        if topic in cls._disinterested_topics:
            return True

        last_recalled = cls._recently_recalled_topics.get(topic)
        if not last_recalled:
            return False

        now_ms = int(time.time() * 1000)
        return (now_ms - last_recalled) < cls.SUPPRESSION_WINDOW_MS

    @classmethod
    def record_recall(cls, topic: str) -> None:
        cls._recently_recalled_topics[topic] = int(time.time() * 1000)

    @classmethod
    def mark_disinterest(cls, topic: str) -> None:
        cls._disinterested_topics.add(topic)

    @classmethod
    def clear(cls) -> None:
        cls._recently_recalled_topics.clear()
        cls._disinterested_topics.clear()
