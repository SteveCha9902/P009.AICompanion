import re
from typing import List, Tuple, Optional
from app.domain.awareness.awareness_context import SceneObjectType

class DeicticResolutionEngine:
    """
    Dedicated engine for parsing deictic pointers (이거, 저거, 이것, 봐봐, 새로 산 등)
    and intent indicators in user utterances.
    """

    DEICTIC_PATTERNS = [
        r"이거\s*([가-힣\w]*)",
        r"저거\s*([가-힣\w]*)",
        r"이것\s*([가-힣\w]*)",
        r"저것\s*([가-힣\w]*)",
        r"봐봐",
        r"보여\??",
        r"어때\??",
        r"새로\s*(산|들인|산거|산 거)",
        r"이\s*(컵|책|노트북|강아지|고양이|식물|화분|모니터)",
        r"사진\s*봐",
    ]

    REJECTION_PATTERNS = [
        r"아니\b",
        r"아냐\b",
        r"아닌데",
        r"그거 말고",
        r"틀렸어",
        r"그게 아니라",
    ]

    CONFIRMATION_PATTERNS = [
        r"응\b",
        r"맞아\b",
        r"어\b",
        r"그래\b",
        r"맞아 그거야",
        r"정답",
    ]

    OBJECT_KEYWORDS = {
        "컵": SceneObjectType.CUP,
        "커피": SceneObjectType.CUP,
        "음료": SceneObjectType.CUP,
        "머그": SceneObjectType.CUP,
        "책": SceneObjectType.BOOK,
        "교재": SceneObjectType.BOOK,
        "소설": SceneObjectType.BOOK,
        "노트북": SceneObjectType.LAPTOP,
        "컴퓨터": SceneObjectType.LAPTOP,
        "맥북": SceneObjectType.LAPTOP,
        "강아지": SceneObjectType.PET,
        "고양이": SceneObjectType.PET,
        "반려동물": SceneObjectType.PET,
        "식물": SceneObjectType.PLANT,
        "화분": SceneObjectType.PLANT,
        "꽃": SceneObjectType.PLANT,
        "티비": SceneObjectType.TV,
        "모니터": SceneObjectType.TV,
        "창문": SceneObjectType.WINDOW,
    }

    @classmethod
    def has_deictic_intent(cls, utterance: str) -> bool:
        normalized = utterance.strip()
        for pat in cls.DEICTIC_PATTERNS:
            if re.search(pat, normalized):
                return True
        return False

    @classmethod
    def detect_explicit_object_mention(cls, utterance: str) -> Optional[SceneObjectType]:
        for keyword, obj_type in cls.OBJECT_KEYWORDS.items():
            if keyword in utterance:
                return obj_type
        return None

    @classmethod
    def is_user_rejecting(cls, utterance: str) -> bool:
        for pat in cls.REJECTION_PATTERNS:
            if re.search(pat, utterance):
                return True
        return False

    @classmethod
    def is_user_confirming(cls, utterance: str) -> bool:
        for pat in cls.CONFIRMATION_PATTERNS:
            if re.search(pat, utterance):
                return True
        return False
