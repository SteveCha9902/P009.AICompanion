from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class CharacterTemplate:
    """
    Template baseline configuration for creating new characters.
    Provides archetype defaults for traits, values, speech, and relationship.
    """
    template_id: str
    name: str
    description: str
    default_role_title: str
    default_mbti: str
    base_traits: Dict[str, float] = field(default_factory=dict)
    base_values: Dict[str, float] = field(default_factory=dict)
    default_speaking_style: str = "friendly_natural"
    default_relationship_type: str = "acquaintance"
    default_avatar_preset: str = "casual_female_01"
    default_voice_id: str = "female_korean_01"
