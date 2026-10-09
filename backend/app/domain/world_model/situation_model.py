from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time

class SituationHypothesis(BaseModel):
    hypothesis_id: str
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    conflicting_evidence: List[str] = Field(default_factory=list)

class AnticipatedSupportOpportunity(BaseModel):
    opportunity_id: str
    title: str
    target_event: str
    probability: float = Field(ge=0.0, le=1.0)
    suggested_support: str
    is_hedged: bool = True # Prediction != Fact compliance
    hedged_phrasing: str = ""

class LifeRoutine(BaseModel):
    routine_id: str
    activity_type: str # MEAL, EXERCISE, SLEEP, WORK, REST
    time_window: str   # e.g. "15:00-16:00"
    frequency_per_week: int = Field(ge=1, le=7)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)

class EnvironmentalFactors(BaseModel):
    time_of_day: str = "AFTERNOON" # MORNING, AFTERNOON, EVENING, NIGHT
    user_fatigue_level: str = "NORMAL" # LOW, NORMAL, HIGH
    physical_context: str = "HOME" # HOME, OFFICE, OUTDOORS

class SituationModel(BaseModel):
    user_id: str
    current_focus: str = "General daily life"
    active_life_chapter: str = "Daily Life Routine"
    hypotheses: List[SituationHypothesis] = Field(default_factory=list)
    active_routines: List[LifeRoutine] = Field(default_factory=list)
    support_opportunities: List[AnticipatedSupportOpportunity] = Field(default_factory=list)
    environmental_factors: EnvironmentalFactors = Field(default_factory=EnvironmentalFactors)
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
