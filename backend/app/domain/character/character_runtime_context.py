from dataclasses import dataclass, field
from typing import Optional, Any
from app.domain.character.character_identity import CharacterIdentity
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.voice.voice_profile import VoiceProfile


@dataclass(frozen=True)
class CharacterScope:
    """
    Minimal Runtime Boundary unit for multi-character isolation.
    Binds a specific user and their companion instance.
    """
    user_id: str
    companion_id: str

    @property
    def character_id(self) -> str:
        """Alias for compatibility with high-level character domain semantics."""
        return self.companion_id


@dataclass(frozen=True)
class CharacterMemoryScope:
    """
    Defines memory boundary and retrieval namespace for a character.
    """
    companion_id: str
    namespace: str = "default"


@dataclass(frozen=True)
class CharacterAvatarProfile:
    """
    Visual identity and presentation baseline for the character avatar.
    """
    avatar_type: str = "2d_character"
    visual_style: str = "anime"
    default_expression: str = "neutral"
    default_motion: str = "idle"


from app.domain.character.presentation_profile import CharacterPresentationProfile


@dataclass(frozen=True)
class CharacterRuntimeContext:
    """
    Stable, immutable character definition context.
    Provides complete identity, personality, voice, avatar, memory scope, and presentation profile for an interaction.
    """
    scope: CharacterScope
    identity: CharacterIdentity
    personality: PersonalityProfile
    memory_scope: CharacterMemoryScope
    voice_profile: VoiceProfile
    avatar_profile: CharacterAvatarProfile
    presentation: Optional[CharacterPresentationProfile] = None


@dataclass
class CharacterRuntimeState:
    """
    Dynamic cognitive evolution snapshot during/after an interaction.
    Note: This is a runtime snapshot container, NOT a replacement for DB persistence models.
    """
    scope: CharacterScope
    emotion: Optional[Any] = None
    relationship: Optional[Any] = None
    growth: Optional[Any] = None
    agency: Optional[Any] = None
    interaction: Optional[Any] = None
