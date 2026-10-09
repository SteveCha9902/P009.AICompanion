from dataclasses import dataclass
from typing import Optional
from app.domain.character.character_dna import CharacterDNA


@dataclass(frozen=True)
class CharacterCreationResult:
    """
    Result returned upon successful character creation.
    """
    companion_id: str
    user_id: str
    name: str
    role_title: str
    dna: CharacterDNA
    is_active: bool = False
    status: str = "created"
    message: str = "Character created successfully"
