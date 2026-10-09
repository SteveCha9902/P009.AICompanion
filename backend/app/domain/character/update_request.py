from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class CharacterUpdateRequest:
    """
    Domain input payload for evolving/updating an existing companion character.
    """
    user_id: str
    companion_id: str
    role_title: Optional[str] = None
    mbti: Optional[str] = None
    personality_keywords: Optional[List[str]] = None
    speaking_style: Optional[str] = None
    voice_id: Optional[str] = None
    avatar_preset: Optional[str] = None
    origin_story: Optional[str] = None
