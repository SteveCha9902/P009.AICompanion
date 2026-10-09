from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time

class FacialEmotionType(str, Enum):
    SMILING = "SMILING"
    NEUTRAL = "NEUTRAL"
    FOCUSED = "FOCUSED"
    CONFUSED = "CONFUSED"
    THINKING = "THINKING"
    FATIGUED = "FATIGUED"
    SURPRISED = "SURPRISED"
    UNKNOWN = "UNKNOWN"

class SceneObjectType(str, Enum):
    CUP = "CUP"
    FOOD = "FOOD"
    BOOK = "BOOK"
    LAPTOP = "LAPTOP"
    PET = "PET"
    PLANT = "PLANT"
    TV = "TV"
    WINDOW = "WINDOW"
    PHONE = "PHONE"
    NOTEBOOK = "NOTEBOOK"
    OTHER = "OTHER"

class VisualFocusTarget(str, Enum):
    USER_FACE = "USER_FACE"
    CUP = "CUP"
    LAPTOP = "LAPTOP"
    PET = "PET"
    BOOK = "BOOK"
    PLANT = "PLANT"
    WINDOW = "WINDOW"
    NONE = "NONE"

class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class DetectedObject(BaseModel):
    type: SceneObjectType
    confidence: float = Field(ge=0.0, le=1.0)
    label: str = ""
    bbox: Optional[BoundingBox] = None

class UserAwarenessState(BaseModel):
    user_presence: bool = False
    face_detected: bool = False
    gaze_direction: str = "toward_camera" # toward_camera, away, screen, looking_down
    attention_level: float = Field(default=0.5, ge=0.0, le=1.0)
    facial_emotion: FacialEmotionType = FacialEmotionType.NEUTRAL
    emotion_confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    user_appearance: str = ""
    clothing: str = ""

class EnvironmentAwarenessState(BaseModel):
    detected_objects: List[DetectedObject] = Field(default_factory=list)
    scene_description: str = ""
    ambient_light: str = "normal" # bright, normal, dim

class AwarenessContext(BaseModel):
    user_state: UserAwarenessState = Field(default_factory=UserAwarenessState)
    environment_state: EnvironmentAwarenessState = Field(default_factory=EnvironmentAwarenessState)
    focus_target: VisualFocusTarget = VisualFocusTarget.USER_FACE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    awareness_timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    @property
    def age_ms(self) -> int:
        return max(0, int(time.time() * 1000) - self.awareness_timestamp_ms)

    @property
    def is_fresh(self) -> bool:
        # Freshness threshold: 10 seconds (10,000ms)
        return self.age_ms <= 10000

    def get_high_confidence_objects(self, min_confidence: float = 0.70) -> List[DetectedObject]:
        """Returns only objects that exceed the minimum confidence threshold to prevent false claims."""
        return [obj for obj in self.environment_state.detected_objects if obj.confidence >= min_confidence]
