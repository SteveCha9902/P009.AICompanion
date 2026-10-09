from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ImportantEventDTO(BaseModel):
    event: str
    importance: float = Field(default=0.8, ge=0.0, le=1.0)

class EmotionalPatternDTO(BaseModel):
    trend: str = "neutral" # e.g. positive, negative, mixed, fluctuating, calm
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    primary_triggers: List[str] = Field(default_factory=list)

class RelationshipInsightDTO(BaseModel):
    suggested_behavior: str = "maintain_supportive_bond"
    intimacy_shift: float = 0.0

class MemoryCandidateDTO(BaseModel):
    content: str
    importance: float = Field(default=0.75, ge=0.0, le=1.0)
    memory_type: str = "CHARACTER_INTERPRETATION"

class ReflectionResult(BaseModel):
    """
    Structured Output contract for the Reflection LLM Engine.
    Free-form unstructured text is strictly prohibited.
    """
    summary: str
    important_events: List[ImportantEventDTO] = Field(default_factory=list)
    emotional_pattern: EmotionalPatternDTO = Field(default_factory=EmotionalPatternDTO)
    relationship_insight: RelationshipInsightDTO = Field(default_factory=RelationshipInsightDTO)
    memory_candidates: List[MemoryCandidateDTO] = Field(default_factory=list)
    behavioral_hints: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
