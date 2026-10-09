from typing import List, Optional
from pydantic import BaseModel, Field


class CharacterScopeRequiredError(ValueError):
    """Raised when an operation requires a valid companion_id but none was provided (Fail-Closed)."""
    pass


class CharacterMemoryScope(BaseModel):
    """
    Explicit Logical Scope for Character-Specific Memory Operations.
    Enforces Rule 1 & Rule 2: (user_id, companion_id) must be fully qualified.
    """
    user_id: str = Field(..., description="Unique ID of the user")
    companion_id: str = Field(..., description="Unique ID of the specific companion/character")

    def validate_scope(self) -> bool:
        if not self.companion_id or self.companion_id.strip() == "":
            raise CharacterScopeRequiredError(
                "CharacterMemoryScope requires a non-empty companion_id. Fail-Closed policy enforced."
            )
        if not self.user_id or self.user_id.strip() == "":
            raise CharacterScopeRequiredError(
                "CharacterMemoryScope requires a non-empty user_id. Fail-Closed policy enforced."
            )
        return True

    @property
    def cache_key_prefix(self) -> str:
        return f"p009:memory:{self.user_id}:{self.companion_id}"


class UserGlobalMemoryScope(BaseModel):
    """
    Scope for User-Global Memory (User profile, global preferences).
    Not bound to a specific character.
    """
    user_id: str = Field(..., description="Unique ID of the user")


class SharedExperienceScope(BaseModel):
    """
    Scope for explicitly shared memories across designated participants.
    """
    user_id: str = Field(..., description="Unique ID of the user")
    participants: List[str] = Field(default_factory=list, description="List of companion_ids with explicit access")
    visibility: str = Field(default="shared", description="Visibility level ('shared', 'public')")
