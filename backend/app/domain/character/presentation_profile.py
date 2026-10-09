from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class VoiceProfileConfig:
    """Voice rendering configuration for character."""
    provider: str = "OPENAI"
    voice_id: str = "nova"
    persona_type: str = "WARM_COMPANION"
    speaking_rate: float = 1.0
    pitch_offset: float = 0.0
    warmth: float = 0.85
    energy: float = 0.60
    empathy: float = 0.90


@dataclass(frozen=True)
class AvatarProfileConfig:
    """Avatar visual style and animation baseline."""
    avatar_id: str = "genie_default"
    visual_style: str = "warm_wife_2d"
    default_expression: str = "affectionate"
    default_motion: str = "gentle_sway"
    portrait_path: str = "assets/avatar_characters/genie_v2_neutral.jpg"


@dataclass(frozen=True)
class ExpressionProfileConfig:
    """Facial expression and eye contact style."""
    style: str = "warm_affectionate"
    gaze_style: str = "loving_eye_contact"
    available_expressions: List[str] = field(default_factory=lambda: [
        "neutral", "happy", "affectionate", "surprised", "thinking", "caring"
    ])


@dataclass(frozen=True)
class GestureProfileConfig:
    """Body gesture and motion style."""
    style: str = "soft_intimate"
    frequency: str = "natural"
    available_gestures: List[str] = field(default_factory=lambda: [
        "idle", "gentle_nod", "soft_wave", "caring_tilt", "close_hand_gesture"
    ])


@dataclass(frozen=True)
class CharacterPresentationProfile:
    """
    Immutable representation of a Character's external presentation identity.
    Decoupled from internal Personality / Cognitive memory states.
    """
    companion_id: str
    voice: VoiceProfileConfig
    avatar: AvatarProfileConfig
    expression: ExpressionProfileConfig
    gesture: GestureProfileConfig


@dataclass(frozen=True)
class CharacterPresentationContext:
    """
    Resolved runtime container ready for mobile avatar and speech synthesis rendering.
    """
    companion_id: str
    voice: VoiceProfileConfig
    avatar: AvatarProfileConfig
    expression: ExpressionProfileConfig
    gesture: GestureProfileConfig

    def to_dict(self) -> Dict[str, Any]:
        return {
            "companion_id": self.companion_id,
            "voice": {
                "provider": self.voice.provider,
                "voice_id": self.voice.voice_id,
                "persona_type": self.voice.persona_type,
                "speaking_rate": self.voice.speaking_rate,
                "pitch_offset": self.voice.pitch_offset,
                "warmth": self.voice.warmth,
                "energy": self.voice.energy,
                "empathy": self.voice.empathy,
            },
            "avatar": {
                "avatar_id": self.avatar.avatar_id,
                "visual_style": self.avatar.visual_style,
                "default_expression": self.avatar.default_expression,
                "default_motion": self.avatar.default_motion,
            },
            "expression": {
                "style": self.expression.style,
                "gaze_style": self.expression.gaze_style,
                "available_expressions": self.expression.available_expressions,
            },
            "gesture": {
                "style": self.gesture.style,
                "frequency": self.gesture.frequency,
                "available_gestures": self.gesture.available_gestures,
            }
        }
