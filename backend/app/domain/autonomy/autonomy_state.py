from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
from app.domain.cognitive.decision_types import BehaviorIntent

class AutonomyMode(str, Enum):
    PASSIVE = "PASSIVE"         # 수동 모드: 사용자가 부를 때만 반응
    RESPONSIVE = "RESPONSIVE"   # 일반 반응 모드: 대화 흐름에 따른 자연스러운 응답
    COMPANION = "COMPANION"     # 동반자 모드: 침묵과 부드러운 관심의 균형
    PROACTIVE = "PROACTIVE"     # 능동 모드: 적절한 타이밍의 자율 안부 및 제안

class ActionCandidate(BaseModel):
    intent: BehaviorIntent
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = ""

class AutonomyDecision(BaseModel):
    selected_action: BehaviorIntent
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    candidate_actions: List[ActionCandidate] = Field(default_factory=list)
    mode: AutonomyMode = AutonomyMode.COMPANION
    internal_trace: str = ""        # Developer / engine debug log (Metrics, weights)
    user_facing_reason: str = ""    # Gentle human-readable explanation
    prompt_directive: str = ""
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
