from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class CharacterCreationRequest:
    """
    User domain input for creating a new companion character.
    """
    user_id: str
    name: str
    template_id: str = "custom"
    role_title: Optional[str] = "AI Companion"
    tagline: Optional[str] = None
    relationship_type: Optional[str] = "family"
    mbti: Optional[str] = "INFJ"
    personality_keywords: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    speaking_style: Optional[str] = None
    speech_profile: Optional[dict] = field(default_factory=dict)
    voice_id: Optional[str] = None
    avatar_preset: Optional[str] = None
    behavior_rules: List[str] = field(default_factory=list)
    origin_story: Optional[str] = None
