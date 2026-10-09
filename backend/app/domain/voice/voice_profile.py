from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import enum

class VoicePersonaType(str, enum.Enum):
    CALM_MENTOR = "CALM_MENTOR"             # 차분함, 신뢰감, 안정된 저음
    WARM_COMPANION = "WARM_COMPANION"       # 공감, 따뜻함, 부드러운 톤 (Genie 기본)
    ENERGETIC_GUIDE = "ENERGETIC_GUIDE"     # 활발함, 에너지, 밝은 하이톤
    PROFESSIONAL_ADVISOR = "PROFESSIONAL_ADVISOR" # 명확함, 정확한 발음, 정중한 톤

class VoiceProviderType(str, enum.Enum):
    OPENAI = "OPENAI"
    ELEVENLABS = "ELEVENLABS"
    AZURE = "AZURE"
    GOOGLE = "GOOGLE"
    CARTESIA = "CARTESIA"
    MOCK = "MOCK"

class VoiceProfile(BaseModel):
    voice_id: str = Field(default="genie_warm_v1", description="Unique Voice Identifier")
    persona_type: VoicePersonaType = Field(default=VoicePersonaType.WARM_COMPANION)
    provider: VoiceProviderType = Field(default=VoiceProviderType.OPENAI)
    
    # Core Acoustic Dimensions (0.0 ~ 1.0)
    warmth: float = Field(default=0.85, ge=0.0, le=1.0)
    energy: float = Field(default=0.60, ge=0.0, le=1.0)
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    empathy: float = Field(default=0.90, ge=0.0, le=1.0)
    
    # Base Prosody Modifiers
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0, description="Base speed multiplier (1.0 = normal)")
    pitch_offset: float = Field(default=0.0, ge=-12.0, le=12.0, description="Pitch shift in semitones")
    breathiness: float = Field(default=0.2, ge=0.0, le=1.0)

class SpeechStyleParameters(BaseModel):
    """
    Dynamic Prosody & Acoustic Parameters modulated per utterance.
    """
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch_offset: float = Field(default=0.0, ge=-12.0, le=12.0)
    volume_gain_db: float = Field(default=0.0, ge=-20.0, le=10.0)
    energy: float = Field(default=0.6, ge=0.0, le=1.0)
    warmth: float = Field(default=0.8, ge=0.0, le=1.0)
    pause_multiplier: float = Field(default=1.0, ge=0.5, le=2.5, description="Silence duration multiplier between sentences")
    ssml_style: Optional[str] = Field(default="chat", description="Provider SSML style (e.g. cheerful, empathetic, calm)")
    emphasis_words: List[str] = Field(default_factory=list)

class AudioSynthesisResult(BaseModel):
    audio_format: str = "mp3"
    audio_base64: Optional[str] = None
    duration_sec: float = 0.0
    visemes: List[Dict[str, Any]] = Field(default_factory=list)
    voice_profile_used: VoiceProfile
    applied_style: SpeechStyleParameters
