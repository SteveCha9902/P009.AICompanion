from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from app.domain.character.character_identity import CharacterIdentity
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.character.character_values import CharacterValues


@dataclass(frozen=True)
class CharacterDNA:
    """
    Immutable Core DNA representing fundamental character nature and traits.
    Decoupled from dynamic mutable runtime state.
    """
    identity: CharacterIdentity
    personality: PersonalityProfile
    values: CharacterValues
    speaking_style: str = "friendly_natural"
    avatar_preset: str = "default_avatar"
    voice_id: str = "female_korean_01"
    tagline: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    speech_profile: Dict[str, Any] = field(default_factory=dict)
    behavior_rules: List[str] = field(default_factory=list)
    emotion_baseline: Dict[str, float] = field(default_factory=dict)
    relationship_defaults: Dict[str, Any] = field(default_factory=dict)
