from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CharacterSummary:
    """
    Lightweight domain summary model for character list and discovery.
    Decoupled from heavy runtime context and API presentation schemas.
    """
    companion_id: str
    name: str
    role_title: Optional[str] = "AI Companion"
    avatar_preview: Optional[str] = None
    voice_name: Optional[str] = None
    is_active: bool = False
