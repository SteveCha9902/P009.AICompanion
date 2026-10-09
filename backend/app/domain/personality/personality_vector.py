from typing import Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import time

class CharacterDNA(BaseModel):
    """
    Core immutable identity DNA of the Companion (Long-term anchor).
    Continuous 7-Axis Personality Vector (0.0 ~ 1.0).
    """
    warmth: float = Field(default=0.92, ge=0.0, le=1.0)       # 따뜻함, 다정함, 친절도
    humor: float = Field(default=0.35, ge=0.0, le=1.0)        # 위트, 유머, 장난기
    curiosity: float = Field(default=0.80, ge=0.0, le=1.0)    # 호기심, 지적 탐구심
    empathy: float = Field(default=0.95, ge=0.0, le=1.0)      # 공감 능력, 배려
    playfulness: float = Field(default=0.30, ge=0.0, le=1.0)  # 명랑함, 발랄함
    formality: float = Field(default=0.30, ge=0.0, le=1.0)    # 격식, 정중함
    optimism: float = Field(default=0.85, ge=0.0, le=1.0)     # 낙관성, 긍정성

    companion_id: str = "default_companion"
    version: int = 1

    @classmethod
    def default_companion_dna(cls) -> "CharacterDNA":
        return cls(
            warmth=0.92,
            humor=0.35,
            curiosity=0.80,
            empathy=0.95,
            playfulness=0.30,
            formality=0.30,
            optimism=0.85
        )

class CrossModalPersonalityManifest(BaseModel):
    """
    Synchronized personality manifestation across LLM, Voice, and Avatar.
    """
    # 1. LLM Tone Directives
    tone_description: str
    key_phrase_guidance: str

    # 2. Voice Parameters
    speech_rate: float = 1.0
    speech_pitch: float = 1.0
    smile_voice_intensity: float = 0.8 # Warmth drives smile voice
    pause_duration_scale: float = 1.0

    # 3. Avatar Physical Parameters
    smile_weight_boost: float = 0.25
    head_tilt_frequency: float = 0.35
    breathing_stability: float = 0.90
