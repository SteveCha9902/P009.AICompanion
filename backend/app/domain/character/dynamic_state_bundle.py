import logging
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from app.domain.memory.character_memory_scope import CharacterScopeRequiredError

logger = logging.getLogger(__name__)


class CharacterDynamicStateScope(BaseModel):
    """
    Immutable Scope for all Multi-Character Dynamic State operations (Emotion, Relationship, Growth, Agency, Presence).
    Enforces (user_id, companion_id) logical boundary and Fail-Closed policy.
    """
    user_id: str = Field(..., description="Unique ID of the user")
    companion_id: str = Field(..., description="Unique ID of the target companion/character")

    def validate_scope(self) -> bool:
        if not self.companion_id or self.companion_id.strip() == "":
            raise CharacterScopeRequiredError(
                "CharacterDynamicStateScope requires a non-empty companion_id. Fail-Closed policy enforced."
            )
        if not self.user_id or self.user_id.strip() == "":
            raise CharacterScopeRequiredError(
                "CharacterDynamicStateScope requires a non-empty user_id. Fail-Closed policy enforced."
            )
        return True

    def build_cache_key(self, namespace: str) -> str:
        return build_character_state_cache_key(namespace, self.user_id, self.companion_id)


def build_character_state_cache_key(namespace: str, user_id: str, companion_id: str) -> str:
    """Standardized multi-character state cache key builder."""
    if not companion_id:
        raise CharacterScopeRequiredError("Cannot build cache key without companion_id.")
    return f"p009:{namespace}:{user_id}:{companion_id}"


class CharacterDynamicStateBundle(BaseModel):
    """
    Logical bundle of all dynamic states associated with a single CharacterScope.
    Guarantees homogeneous character identity across Emotion, Relationship, Growth, Agency, and Presence.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    scope: CharacterDynamicStateScope
    emotion_state: Optional[Any] = None
    relationship_state: Optional[Any] = None
    growth_state: Optional[Any] = None
    agency_state: Optional[Any] = None
    presence_state: Optional[Any] = None

    def validate_consistency(self) -> bool:
        """
        Validates that all loaded sub-states belong strictly to the pinned companion_id.
        Prevents cross-character state contamination.
        """
        self.scope.validate_scope()
        target_cid = self.scope.companion_id

        states = [
            ("emotion", self.emotion_state),
            ("relationship", self.relationship_state),
            ("growth", self.growth_state),
            ("agency", self.agency_state),
            ("presence", self.presence_state)
        ]

        for name, state in states:
            if state is not None:
                state_cid = getattr(state, "companion_id", None)
                if state_cid and state_cid != target_cid:
                    raise ValueError(
                        f"State inconsistency in bundle! Expected companion_id='{target_cid}' "
                        f"for '{name}', found '{state_cid}'"
                    )
        return True
