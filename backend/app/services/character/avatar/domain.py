from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AvatarBehavioralState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    PRE_EXPRESSION = "pre_expression"
    SPEAKING = "speaking"
    SETTLING = "settling"

class VisemeType(str, Enum):
    CLOSED = "closed"
    A = "viseme_a"
    E = "viseme_e"
    I = "viseme_i"
    O = "viseme_o"
    U = "viseme_u"

class AvatarMotion(BaseModel):
    """
    Standard Motion Definition in Motion Library V1 (Sprint 45).
    """
    motion_id: str
    category: str
    head_tilt_delta: float = 0.0
    head_pitch_delta: float = 0.0
    head_yaw_delta: float = 0.0
    nod_intensity_delta: float = 0.0
    body_lean_delta: float = 0.0
    eye_contact_bias: float = 0.0
    smile_delta: float = 0.0
    duration_ms: int = 1500

class MotionParameters(BaseModel):
    """
    Active Motion Parameters with Randomization Jitter.
    """
    active_motion_id: str = "DEFAULT_IDLE"
    head_tilt: float = 0.0
    head_pitch: float = 0.0
    head_yaw: float = 0.0
    nod_intensity: float = 0.0
    body_lean: float = 0.0
    jitter_factor: float = 1.0

class RelationshipParameters(BaseModel):
    """
    Standard Relationship Parameters DTO for relational embodiment.
    """
    familiarity: float = Field(default=0.5, ge=0.0, le=1.0)
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    warmth: float = Field(default=0.5, ge=0.0, le=1.0)
    engagement: float = Field(default=0.6, ge=0.0, le=1.0)

class BehaviorParameters(BaseModel):
    """
    Standard Embodied Behavior Parameters DTO.
    """
    attention_level: float = Field(default=0.8, ge=0.0, le=1.0)
    eye_contact: float = Field(default=0.85, ge=0.0, le=1.0)
    head_tilt: float = Field(default=0.0, ge=-30.0, le=30.0)
    nod_intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    body_lean: float = Field(default=0.0, ge=-1.0, le=1.0)
    curiosity_level: float = Field(default=0.5, ge=0.0, le=1.0)
    thinking_intensity: float = Field(default=0.0, ge=0.0, le=1.0)

class SpeechParameters(BaseModel):
    """
    Standard Speech Parameters DTO for real-time lip-sync and audio embodiment.
    """
    is_speaking: bool = False
    mouth_open: float = Field(default=0.0, ge=0.0, le=1.0)
    viseme: VisemeType = VisemeType.CLOSED
    speech_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    speech_progress: float = Field(default=0.0, ge=0.0, le=1.0)

class FaceParameters(BaseModel):
    """
    Standard Face Engine DTO for renderer-independent real-time control.
    """
    eye_openness: float = Field(default=0.9, ge=0.0, le=1.0)
    blink_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    eye_direction_x: float = Field(default=0.0, ge=-1.0, le=1.0)
    eye_direction_y: float = Field(default=0.0, ge=-1.0, le=1.0)
    mouth_open: float = Field(default=0.0, ge=0.0, le=1.0)
    smile_strength: float = Field(default=0.3, ge=0.0, le=1.0)
    brow_raise: float = Field(default=0.0, ge=-1.0, le=1.0)
    head_pitch: float = Field(default=0.0, ge=-30.0, le=30.0)
    head_yaw: float = Field(default=0.0, ge=-30.0, le=30.0)
    head_roll: float = Field(default=0.0, ge=-30.0, le=30.0)
    warmth: float = Field(default=0.5, ge=0.0, le=1.0)

class ContinuousEmotionVector(BaseModel):
    """
    Continuous multi-dimensional emotional state representation.
    """
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    arousal: float = Field(default=0.5, ge=0.0, le=1.0)
    warmth: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)

class ExpressionParameters(BaseModel):
    """
    Renderer-agnostic facial expression parameters.
    """
    smile_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    eye_softness: float = Field(default=0.5, ge=0.0, le=1.0)
    eye_openness: float = Field(default=1.0, ge=0.0, le=1.0)
    blink_value: float = Field(default=0.0, ge=0.0, le=1.0)
    brow_raise: float = Field(default=0.0, ge=-1.0, le=1.0)
    mouth_open: float = Field(default=0.0, ge=0.0, le=1.0)
    viseme: VisemeType = VisemeType.CLOSED
    head_pitch: float = Field(default=0.0, ge=-30.0, le=30.0)
    head_yaw: float = Field(default=0.0, ge=-30.0, le=30.0)
    head_roll: float = Field(default=0.0, ge=-30.0, le=30.0)
    warmth_alpha: float = Field(default=0.5, ge=0.0, le=1.0)

class AvatarGesture(BaseModel):
    """
    Individual gesture item within a multi-gesture stack.
    """
    gesture_type: str
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    blend_weight: float = Field(default=1.0, ge=0.0, le=1.0)

class AvatarBehaviorPlan(BaseModel):
    """
    Complete synchronous behavior plan emitted by AvatarBehaviorController.
    """
    state: AvatarBehavioralState = AvatarBehavioralState.IDLE
    expression: ExpressionParameters = Field(default_factory=ExpressionParameters)
    face_parameters: FaceParameters = Field(default_factory=FaceParameters)
    speech_parameters: SpeechParameters = Field(default_factory=SpeechParameters)
    behavior_parameters: BehaviorParameters = Field(default_factory=BehaviorParameters)
    relationship_parameters: RelationshipParameters = Field(default_factory=RelationshipParameters)
    motion_parameters: MotionParameters = Field(default_factory=MotionParameters)
    selected_motion: Optional[AvatarMotion] = None
    active_gestures: List[AvatarGesture] = Field(default_factory=list)
    attention_level: float = Field(default=0.8, ge=0.0, le=1.0)
    transition_duration_ms: int = Field(default=300, ge=0, le=2000)
    speech_sync_ready: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
