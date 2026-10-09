from typing import Tuple

class FalseMemoryGuard:
    """
    Prevents dogmatic assertions on unverified or low-confidence memories (< 0.80).
    Enforces soft conjectural phrases ('내가 기억하기로는...', '맞다면...').
    """

    CONFIDENCE_THRESHOLD = 0.80

    @classmethod
    def validate_memory_recall(cls, memory_confidence: float, recall_statement: str) -> Tuple[bool, str]:
        if memory_confidence < cls.CONFIDENCE_THRESHOLD:
            # Must contain soft modal phrase
            has_soft_modal = any(kw in recall_statement for kw in ("기억하기로는", "맞다면", "언뜻", "이야기하셨던 것 같은데", "생각나네요"))
            if not has_soft_modal:
                return (
                    False,
                    f"Memory confidence {memory_confidence:.2f} is below 0.80 without humble conjectural phrasing."
                )
        return (True, "Memory recall passes confidence & humility standard.")
