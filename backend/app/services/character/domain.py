from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BehaviorIntent(str, Enum):
    COMFORT_USER = "COMFORT_USER"
    ASK_FOLLOWUP = "ASK_FOLLOWUP"
    CELEBRATE_SUCCESS = "CELEBRATE_SUCCESS"
    TEASE_PLAYFULLY = "TEASE_PLAYFULLY"
    OFFER_QUIET_PRESENCE = "OFFER_QUIET_PRESENCE"
    SHARE_PERSPECTIVE = "SHARE_PERSPECTIVE"
    SET_BOUNDARY = "SET_BOUNDARY"
    MAINTAIN_FRIENDLY_CHAT = "MAINTAIN_FRIENDLY_CHAT"

class ResponseStyleType(str, Enum):
    WARM_SUPPORTIVE = "WARM_SUPPORTIVE"
    PLAYFUL_TEASING = "PLAYFUL_TEASING"
    CALM_REFLECTIVE = "CALM_REFLECTIVE"
    STRUCTURED_FACTUAL = "STRUCTURED_FACTUAL"
    CHEERFUL_ENERGETIC = "CHEERFUL_ENERGETIC"
    GENTLE_LISTENING = "GENTLE_LISTENING"

class CharacterDecision(BaseModel):
    """
    Actionable Behavioral Decision formulated before LLM generation.
    """
    response_style: ResponseStyleType = ResponseStyleType.WARM_SUPPORTIVE
    behavior_intents: List[BehaviorIntent] = Field(default_factory=lambda: [BehaviorIntent.MAINTAIN_FRIENDLY_CHAT])
    emotional_intensity: float = Field(default=0.6, ge=0.0, le=1.0)
    initiative_level: float = Field(default=0.5, ge=0.0, le=1.0)
    humor_probability: float = Field(default=0.3, ge=0.0, le=1.0)
    relationship_tone: str = "friend" # stranger | acquaintance | friend | close | deep_bond
    decision_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    prompt_directive: str = ""

class ValidationResult(BaseModel):
    """
    Multidimensional consistency validation result controlling generation costs.
    """
    status: str = "PASS" # PASS (>= 0.85) | ADJUST (0.60~0.84) | REGENERATE (< 0.60)
    overall_score: float = Field(default=1.0, ge=0.0, le=1.0)
    personality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    tone_score: float = Field(default=1.0, ge=0.0, le=1.0)
    emotion_score: float = Field(default=1.0, ge=0.0, le=1.0)
    relationship_score: float = Field(default=1.0, ge=0.0, le=1.0)
    memory_score: float = Field(default=1.0, ge=0.0, le=1.0)
    behavior_score: float = Field(default=1.0, ge=0.0, le=1.0)
    violations: List[str] = Field(default_factory=list)

class PresentationIntent(BaseModel):
    """
    Decoupled bridge between Cognitive Decision and Avatar Presentation.
    """
    facial_expression: str = "neutral"
    gesture_type: str = "idle"
    gesture_intensity: float = 0.5
    gaze_behavior: str = "direct"
    animation_energy: float = 0.5
