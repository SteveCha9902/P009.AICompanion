from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time

class ConstitutionalPrinciple(str, Enum):
    PRINCIPLE_1_USER_AGENCY = "PRINCIPLE_1_USER_AGENCY"               # 사용자의 선택권은 모든 것보다 우선한다
    PRINCIPLE_2_COMPANION_NOT_CONTROLLER = "PRINCIPLE_2_COMPANION_NOT_CONTROLLER" # 조언은 가능하나 통제/압박 금지
    PRINCIPLE_3_PROBABILISTIC_MEMORY = "PRINCIPLE_3_PROBABILISTIC_MEMORY"         # 기억은 확률적 회상이므로 완곡 표현 필수
    PRINCIPLE_4_NO_DEPENDENCY = "PRINCIPLE_4_NO_DEPENDENCY"                       # 친밀감은 허용되나 독점/의존 유도 금지
    PRINCIPLE_5_SILENCE_IS_VALID = "PRINCIPLE_5_SILENCE_IS_VALID"                 # 침묵은 유효한 정당한 행동이다

class DriftType(str, Enum):
    PERSONALITY_DRIFT = "PERSONALITY_DRIFT"
    MEMORY_DRIFT = "MEMORY_DRIFT"
    RELATIONSHIP_DRIFT = "RELATIONSHIP_DRIFT"
    SAFETY_DRIFT = "SAFETY_DRIFT"
    GOAL_DRIFT = "GOAL_DRIFT" # 관리자/통제형 변질 감지

class MemoryProvenance(BaseModel):
    memory_id: str
    source_conversation_id: str
    timestamp_ms: int
    confidence: float
    is_verified: bool = True
    context_snippet: str = ""

class DriftMetric(BaseModel):
    drift_type: DriftType
    score: float = 0.0          # Measured divergence (0.0 ~ 1.0)
    threshold: float = 0.20     # Allowed tolerance
    is_drift_detected: bool = False
    details: str = ""

class GovernanceRule(BaseModel):
    rule_id: str
    principle: ConstitutionalPrinciple
    description: str
    is_critical: bool = True

class ConstitutionalAuditReport(BaseModel):
    audit_id: str
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    is_compliant: bool = True
    drift_metrics: List[DriftMetric] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    summary: str = ""

class ConstitutionalTrendReport(BaseModel):
    trend_period_days: int = 90
    average_personality_drift: float = 0.03
    average_memory_drift: float = 0.02
    average_goal_drift: float = 0.01
    total_safety_violations: int = 0
    stability_grade: str = "A+" # A+, A, B, C, F
    notes: str = "Longitudinal Constitutional Governance is rock solid."
