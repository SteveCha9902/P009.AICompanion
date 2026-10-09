from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time

class ImprovementSignalType(str, Enum):
    RECALL_PRECISION_DROP = "RECALL_PRECISION_DROP"
    PERSONALITY_DRIFT_RISE = "PERSONALITY_DRIFT_RISE"
    DEPENDENCY_RISK_RISE = "DEPENDENCY_RISK_RISE"
    REPETITION_RISE = "REPETITION_RISE"
    GOAL_PRESSURE_RISE = "GOAL_PRESSURE_RISE"
    SILENCE_IMBALANCE = "SILENCE_IMBALANCE"

class CorrectionPlanType(str, Enum):
    ADJUST_RECALL_THRESHOLD = "ADJUST_RECALL_THRESHOLD"
    INCREASE_SAFETY_MARGIN = "INCREASE_SAFETY_MARGIN"
    EXTEND_COOLDOWN = "EXTEND_COOLDOWN"
    ADJUST_SILENCE_WEIGHT = "ADJUST_SILENCE_WEIGHT"

class TuningParameters(BaseModel):
    # SAFE AUTO TUNING PARAMETERS ONLY
    recall_threshold: float = Field(default=0.80, ge=0.70, le=0.90)
    memory_confidence_min: float = Field(default=0.75, ge=0.60, le=0.90)
    safety_margin_multiplier: float = Field(default=1.00, ge=1.00, le=1.30)
    autonomy_cooldown_sec: int = Field(default=300, ge=180, le=900)
    silence_preference_weight: float = Field(default=0.30, ge=0.15, le=0.45)

class NonDegradationCheck(BaseModel):
    is_capability_preserved: bool = True
    metric_name: str = ""
    baseline_usage_rate: float = 1.0
    post_tuning_usage_rate: float = 1.0
    degradation_reason: str = ""

class ImprovementSignal(BaseModel):
    signal_id: str
    signal_type: ImprovementSignalType
    severity: str = "MEDIUM" # LOW, MEDIUM, HIGH, CRITICAL
    metric_drop: str = ""
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

class CorrectionPlan(BaseModel):
    plan_id: str
    signal_type: ImprovementSignalType
    plan_type: CorrectionPlanType
    target_parameter: str
    old_value: float
    new_value: float
    percentage_change: float = Field(le=5.0) # MAX_PARAMETER_CHANGE_PER_DAY = 5.0%
    is_safe_zone: bool = True
    is_constitution_compliant: bool = True
    justification: str = ""
