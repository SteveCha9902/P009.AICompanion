from typing import List, Dict, Any
from pydantic import BaseModel, Field

class CharacterGlobalGrowthState(BaseModel):
    """
    Global character growth states across all interactions.
    Immutable Core (Identity/Values) is permanently LOCKED.
    """
    companion_id: str = "genie"
    support_style: str = "EMPATHIC_LISTENER" # EMPATHIC_LISTENER | PRACTICAL_ADVISOR | QUIET_COMPANION
    initiative_tendency: str = "BALANCED" # BALANCED | PROACTIVE | PATIENT
    global_learned_behavior: List[str] = Field(default_factory=list)

class UserRelationshipAdaptationState(BaseModel):
    """
    User-specific conversational preferences and adaptation styles.
    """
    user_id: str = "default_user"
    companion_id: str = "genie"
    preferred_formality: float = Field(default=0.3, ge=0.0, le=1.0)
    preferred_humor: float = Field(default=0.6, ge=0.0, le=1.0)
    preferred_directness: float = Field(default=0.5, ge=0.0, le=1.0)
    support_preference: str = "EMPATHIC_SUPPORT"
    conversation_rhythm: str = "NATURAL"
