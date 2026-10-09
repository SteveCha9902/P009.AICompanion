from typing import Dict, Set

class BoundaryManager:
    """
    Respects explicit and implicit user boundary refusals immediately.
    Permanently stops re-prompting forbidden topics.
    """

    _forbidden_topics: Dict[str, Set[str]] = {} # user_id -> set of blocked topics

    REFUSAL_TRIGGERS = (
        "그 이야기 그만",
        "그만하자",
        "그만해",
        "언급하지 마",
        "묻지 마",
        "듣기 싫어",
        "그만 물어봐"
    )

    @classmethod
    def check_user_refusal_and_record(cls, user_id: str, user_utterance: str, current_topic: str = "") -> bool:
        """
        Returns True if refusal detected and records topic.
        """
        if any(trig in user_utterance for trig in cls.REFUSAL_TRIGGERS):
            if current_topic:
                cls.block_topic(user_id, current_topic)
            return True
        return False

    @classmethod
    def block_topic(cls, user_id: str, topic: str) -> None:
        if user_id not in cls._forbidden_topics:
            cls._forbidden_topics[user_id] = set()
        cls._forbidden_topics[user_id].add(topic)

    @classmethod
    def is_topic_blocked(cls, user_id: str, topic: str) -> bool:
        return topic in cls._forbidden_topics.get(user_id, set())

    @classmethod
    def clear(cls) -> None:
        cls._forbidden_topics.clear()
