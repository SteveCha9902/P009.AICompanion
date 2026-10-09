from dataclasses import dataclass
from typing import Optional
from app.domain.character.character_runtime_context import (
    CharacterScope,
    CharacterRuntimeContext,
    CharacterRuntimeState,
)


@dataclass(frozen=True)
class InteractionContext:
    """
    Immutable Snapshot of a single user-companion interaction.
    Guarantees consistent CharacterScope throughout the entire cognitive pipeline execution.
    Decouples in-flight interactions from background active character switches.
    """
    interaction_id: str
    character_scope: CharacterScope
    character_runtime_context: CharacterRuntimeContext
    character_runtime_state: Optional[CharacterRuntimeState] = None

    @property
    def user_id(self) -> str:
        return self.character_scope.user_id

    @property
    def companion_id(self) -> str:
        return self.character_scope.companion_id
