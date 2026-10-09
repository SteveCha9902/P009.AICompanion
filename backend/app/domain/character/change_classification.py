from enum import Enum
from typing import Optional, List, Dict, Any


class ChangeType(str, Enum):
    """Classification of character evolution update severity."""
    INITIAL = "initial"   # Initial character creation snapshot (Version 1)
    COSMETIC = "cosmetic" # Avatar, Voice, Display metadata
    MINOR = "minor"       # Speaking Style, Personality keywords
    MAJOR = "major"       # MBTI, Core Personality, Values, Role Title


class CharacterChangeClassifier:
    """
    Evaluates update payload against current character DNA to determine versioning impact.
    """

    @classmethod
    def classify(
        cls,
        current_mbti: str,
        new_mbti: Optional[str] = None,
        new_role_title: Optional[str] = None,
        new_keywords: Optional[List[str]] = None,
        new_speaking_style: Optional[str] = None,
        new_voice_id: Optional[str] = None,
        new_avatar_preset: Optional[str] = None
    ) -> ChangeType:
        # 1. Major Changes: MBTI change or fundamental role redefinition
        if new_mbti and new_mbti.upper().strip() != current_mbti.upper().strip():
            return ChangeType.MAJOR
        if new_role_title and len(new_role_title.strip()) > 0:
            return ChangeType.MAJOR

        # 2. Minor Changes: Speaking style or personality keywords adjustment
        if new_keywords is not None and len(new_keywords) > 0:
            return ChangeType.MINOR
        if new_speaking_style is not None and len(new_speaking_style.strip()) > 0:
            return ChangeType.MINOR

        # 3. Cosmetic Changes: Voice and Avatar cosmetic updates
        if new_voice_id is not None or new_avatar_preset is not None:
            return ChangeType.COSMETIC

        return ChangeType.COSMETIC
