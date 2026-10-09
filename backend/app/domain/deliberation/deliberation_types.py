from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
from app.domain.cognitive.decision_types import BehaviorIntent

class CouncilRole(str, Enum):
    MEMORY = "MEMORY"
    RELATIONSHIP = "RELATIONSHIP"
    GOAL = "GOAL"
    WORLD_MODEL = "WORLD_MODEL"
    AUTONOMY = "AUTONOMY"

class UncertaintyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class CouncilOpinion(BaseModel):
    role: CouncilRole
    suggested_intent: BehaviorIntent
    confidence: float = Field(ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=2.0)
    reason: str = ""

class DecisionTrace(BaseModel):
    opinions: List[CouncilOpinion] = Field(default_factory=list)
    conflict_summary: str = ""
    deadlock_resolved_by: Optional[str] = None
    safety_sanction_notes: str = ""
    constitution_sanction_notes: str = ""
    internal_trace: str = ""
    user_facing_summary: str = ""

class FinalCompanionDecision(BaseModel):
    selected_intent: BehaviorIntent
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty_level: UncertaintyLevel = UncertaintyLevel.LOW
    trace: DecisionTrace
    proposed_text: str = ""
    avatar_expression: str = "neutral"
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
