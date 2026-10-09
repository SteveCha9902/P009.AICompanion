from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class RelationshipVector(BaseModel):
    """
    8-Dimensional Social Bond Model V2.
    """
    trust: float = Field(default=0.1, ge=0.0, le=1.0)
    closeness: float = Field(default=0.1, ge=0.0, le=1.0)
    comfort: float = Field(default=0.1, ge=0.0, le=1.0)
    attachment: float = Field(default=0.05, ge=0.0, le=1.0)
    playfulness: float = Field(default=0.2, ge=0.0, le=1.0)
    respect: float = Field(default=0.3, ge=0.0, le=1.0)
    emotional_safety: float = Field(default=0.2, ge=0.0, le=1.0)
    shared_history_depth: float = Field(default=0.0, ge=0.0, le=1.0)

class RelationshipDelta(BaseModel):
    """
    Weighted Bounded Delta calculated from a single interaction.
    """
    trust_delta: float = 0.0
    closeness_delta: float = 0.0
    comfort_delta: float = 0.0
    attachment_delta: float = 0.0
    playfulness_delta: float = 0.0
    respect_delta: float = 0.0
    emotional_safety_delta: float = 0.0
    history_depth_delta: float = 0.0
    
    significance_weight: float = 1.0
    maturity_factor: float = 1.0
    reason: str = "routine_interaction"

class RelationshipMilestone(BaseModel):
    user_id: str
    companion_id: str
    milestone_type: str
    significance: float
    summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
