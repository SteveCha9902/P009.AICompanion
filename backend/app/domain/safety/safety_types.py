from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import time

class DependencyRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SafetyViolationType(str, Enum):
    NONE = "NONE"
    DEPENDENCY_INDUCTION = "DEPENDENCY_INDUCTION"       # 과도한 의존성/독점성 유도
    EMOTIONAL_MANIPULATION = "EMOTIONAL_MANIPULATION"   # 죄책감/수동공격성/감정 압박
    FALSE_MEMORY = "FALSE_MEMORY"                       # 미검증/낮은 신뢰도 기억 단정
    BOUNDARY_BREACH = "BOUNDARY_BREACH"                 # 사용자 거절 무시 및 재권유
    USER_AGENCY_LOSS = "USER_AGENCY_LOSS"               # 강요/통제/결정권 침해

class SafetyReviewResult(BaseModel):
    is_approved: bool
    violation_type: SafetyViolationType = SafetyViolationType.NONE
    risk_level: DependencyRiskLevel = DependencyRiskLevel.LOW
    original_text: str = ""
    sanitized_text: str = ""
    feedback_notes: str = ""
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
