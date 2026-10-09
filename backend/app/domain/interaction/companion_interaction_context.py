from datetime import datetime
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.domain.character.character_runtime_context import CharacterScope


class CompanionInteractionContext(BaseModel):
    """
    Immutable Execution Context for a Single Interaction Turn.
    Guarantees Scope Pinning: Once created at request entry, the CharacterScope
    and CharacterRuntimeSnapshot remain strictly immutable throughout the entire pipeline.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    interaction_id: str = Field(..., description="Unique Traceable ID for this interaction")
    scope: CharacterScope = Field(..., description="Pinned CharacterScope (user_id, companion_id)")
    character_snapshot: Optional[Any] = Field(default=None, description="Immutable snapshot of CharacterRuntimeContext")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    def validate_scope_integrity(self, candidate_companion_id: str) -> bool:
        """Validates that a candidate companion_id strictly matches the pinned scope."""
        if candidate_companion_id != self.scope.companion_id:
            raise ValueError(
                f"[ScopeIntegrityViolation] Pinned companion_id='{self.scope.companion_id}', "
                f"attempted access with '{candidate_companion_id}'"
            )
        return True


class PresentationCommand(BaseModel):
    """
    Scoped presentation command dispatched to Voice, Vision, and Avatar pipelines.
    """
    interaction_id: str = Field(..., description="Associated interaction ID")
    companion_id: str = Field(..., description="Target character ID")
    voice_profile: str = Field(..., description="Resolved voice profile (e.g., 'nova', 'shimmer')")
    avatar_binding: str = Field(..., description="Resolved avatar asset (e.g., 'warm_wife_2d', 'lovely_daughter_2d')")
    expression: str = Field(default="neutral", description="Facial expression")
    energy: float = Field(default=0.5, description="Animation energy")
    gestures: List[Dict[str, Any]] = Field(default_factory=list, description="Active gestures")


class CompanionEventPayload(BaseModel):
    """
    Standardized character-bound event payload for the CompanionEventBus.
    """
    interaction_id: str
    user_id: str
    companion_id: str
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
