from enum import Enum
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import time
from app.domain.awareness.awareness_context import SceneObjectType, BoundingBox

class JointAttentionState(str, Enum):
    NONE = "NONE"                          # 공유 대상 없음 (기본 상태)
    USER_FOCUS = "USER_FOCUS"              # 사용자가 특정 대상에 관심 표현
    SHARED_FOCUS = "SHARED_FOCUS"          # 사용자와 캐릭터가 동일 대상 주목
    DISCUSSING_TARGET = "DISCUSSING_TARGET" # 대상에 대해 활발히 대화 중

class UserConfirmationStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"

class AttentionAnchor(str, Enum):
    USER_FACE = "USER_FACE"
    CENTER = "CENTER"
    LOWER_LEFT = "LOWER_LEFT"
    LOWER_CENTER = "LOWER_CENTER"
    LOWER_RIGHT = "LOWER_RIGHT"
    UPPER_LEFT = "UPPER_LEFT"
    UPPER_RIGHT = "UPPER_RIGHT"

class CandidateFocus(BaseModel):
    object_type: SceneObjectType
    label: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    anchor: AttentionAnchor = AttentionAnchor.CENTER
    bbox: Optional[BoundingBox] = None

class SharedRealityContext(BaseModel):
    state: JointAttentionState = JointAttentionState.NONE
    focus_target: Optional[SceneObjectType] = None
    target_label: str = ""
    target_confidence: float = 0.0
    anchor: AttentionAnchor = AttentionAnchor.USER_FACE
    candidate_targets: List[CandidateFocus] = Field(default_factory=list)
    user_intent: str = ""
    confirmation_status: UserConfirmationStatus = UserConfirmationStatus.UNKNOWN
    shared_attention: bool = False
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    focus_lock_until_ms: int = 0
    last_interaction_time_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    MIN_SHARED_FOCUS_CONFIDENCE: ClassVar[float] = 0.75
    SHARED_ATTENTION_TIMEOUT_MS: ClassVar[int] = 15000 # 15 seconds

    @property
    def is_locked(self) -> bool:
        return int(time.time() * 1000) < self.focus_lock_until_ms

    @property
    def is_timed_out(self) -> bool:
        return (int(time.time() * 1000) - self.last_interaction_time_ms) > self.SHARED_ATTENTION_TIMEOUT_MS

