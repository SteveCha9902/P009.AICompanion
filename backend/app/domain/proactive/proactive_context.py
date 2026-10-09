from enum import Enum
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import time
from app.domain.memory.relationship_memory import MemoryType

class ProactiveTriggerType(str, Enum):
    MEMORY_FOLLOWUP = "MEMORY_FOLLOWUP"     # 과거 기억 기반 후속 안부
    IDLE_PRESENCE = "IDLE_PRESENCE"         # 60초+ 유휴 시 가벼운 동반 발화
    TIME_GREETING = "TIME_GREETING"         # 시간대별 다정한 인사
    OBJECT_REMINISCENCE = "OBJECT_REMINISCENCE" # 카메라 사물 기반 회상

class ProactiveMode(str, Enum):
    NORMAL = "NORMAL" # 30분 1회 쿨다운
    QUIET = "QUIET"   # 하루 1~2회 (6시간 쿨다운)
    OFF = "OFF"       # 능동 발화 완전 비활성화

class ProactiveDialogueStyle(str, Enum):
    GREETING = "GREETING"           # 안부형 ("오늘 하루는 어땠어?")
    REMINISCENCE = "REMINISCENCE"   # 회상형 ("그 식물은 잘 자라고 있어?")
    ENCOURAGEMENT = "ENCOURAGEMENT" # 격려형 ("진행 중인 프로젝트 파이팅이야!")
    OBSERVATION = "OBSERVATION"     # 관찰형 ("오늘 날씨가 참 맑네")

class ProactiveOpportunity(BaseModel):
    id: str = Field(default_factory=lambda: str(time.time()))
    trigger_type: ProactiveTriggerType
    memory_id: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    topic: str
    priority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    dialogue_style: ProactiveDialogueStyle = ProactiveDialogueStyle.GREETING
    suggested_starter: str
    receptiveness_score: float = Field(default=0.8, ge=0.0, le=1.0)
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    # Follow-up window days mapping by Memory Type
    FOLLOWUP_WINDOW_DAYS: ClassVar[Dict[MemoryType, int]] = {
        MemoryType.PET: 5,        # 3~7 days (avg 5)
        MemoryType.PROJECT: 10,   # 7~14 days (avg 10)
        MemoryType.HOBBY: 14,     # 14 days
        MemoryType.OBJECT: 15,    # 10~30 days (avg 15)
        MemoryType.GOAL: 14,      # 14 days
        MemoryType.PLACE: 20,     # 20 days
        MemoryType.EVENT: 7,      # 7 days
        MemoryType.PREFERENCE: 30,# 30 days
        MemoryType.PERSON: 7,     # 7 days
    }
