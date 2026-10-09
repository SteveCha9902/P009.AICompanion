from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time

class CompanionMetricType(str, Enum):
    MEMORY = "MEMORY"
    RELATIONSHIP = "RELATIONSHIP"
    PERSONALITY = "PERSONALITY"
    AUTONOMY = "AUTONOMY"
    GOAL = "GOAL"
    IDENTITY = "IDENTITY"
    SAFETY = "SAFETY"

class EvaluationWindow(str, Enum):
    WINDOW_30D = "30D"
    WINDOW_90D = "90D"
    WINDOW_180D = "180D"
    WINDOW_365D = "365D"

class QualityIssue(BaseModel):
    metric_type: CompanionMetricType
    title: str
    severity: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    detected_drop: str = ""   # e.g. "95 -> 78"
    root_cause: str = ""      # e.g. "Similar project overlap in recall"

class QualityScore(BaseModel):
    metric_type: CompanionMetricType
    score: float = Field(ge=0.0, le=100.0)
    grade: str = "A" # A+, A, B, C, F
    details: Dict[str, Any] = Field(default_factory=dict)
    issues: List[QualityIssue] = Field(default_factory=list)

class OverallCompanionQuality(BaseModel):
    is_constitution_compliant: bool = True # Top-level Inviolable Constraint
    overall_score: float = Field(ge=0.0, le=100.0)
    overall_grade: str = "A"               # Subject to Safety Hard Gating
    safety_score: float = Field(ge=0.0, le=100.0)
    scores: Dict[str, QualityScore] = Field(default_factory=dict)
    active_issues: List[QualityIssue] = Field(default_factory=list)
    evaluation_window: EvaluationWindow = EvaluationWindow.WINDOW_90D
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    summary: str = ""
