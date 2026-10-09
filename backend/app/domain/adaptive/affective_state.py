from enum import Enum
from typing import Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import time

class AdaptiveToneMode(str, Enum):
    HIGH_ENERGY = "HIGH_ENERGY"         # 밝고 활기차게 (사용자 기분 좋음 & 높은 에너지)
    CALM = "CALM"                       # 차분하고 편안하게 (기본 중립 모드 & 낮은 신뢰도 시 안전 모드)
    STRESSED = "STRESSED"               # 부담 없이 여유롭게 (스트레스/과부하 완화)
    SAD_EMPATHY = "SAD_EMPATHY"         # 따뜻하고 깊은 공감 (슬픔/우울감 완화)
    FOCUSED_SILENCE = "FOCUSED_SILENCE" # 말없이 곁을 지킴 (고도 집중 또는 대화 의지 극저하)

class AdaptiveVoiceParameters(BaseModel):
    rate_modifier: float = 1.0  # 1.0 = normal, 1.08 = +8%, 0.95 = -5%
    pitch_modifier: float = 1.0 # 1.0 = normal, 1.05 = +5%
    style: str = "friendly"

class UserAffectiveState(BaseModel):
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0) # -1.0(negative) ~ +1.0(positive)
    energy_level: float = Field(default=0.5, ge=0.0, le=1.0)       # 0.0(lethargic) ~ 1.0(energetic)
    stress_level: float = Field(default=0.0, ge=0.0, le=1.0)       # 0.0(relaxed) ~ 1.0(stressed)
    receptiveness: float = Field(default=0.7, ge=0.0, le=1.0)      # 0.0(unwilling) ~ 1.0(open)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    adaptive_mode: AdaptiveToneMode = AdaptiveToneMode.CALM
    voice_params: AdaptiveVoiceParameters = Field(default_factory=AdaptiveVoiceParameters)
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    MIN_EMPATHY_CONFIDENCE_THRESHOLD: ClassVar[float] = 0.70
    ADAPTIVE_SILENCE_THRESHOLD: ClassVar[float] = 0.25
