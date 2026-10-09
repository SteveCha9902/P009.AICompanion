from typing import Optional
import math
from app.domain.voice.voice_profile import VoiceProfile, SpeechStyleParameters
from app.services.character.avatar.domain import ContinuousEmotionVector

class EmotionalSpeechEngine:
    """
    Translates Continuous Emotion Vectors into dynamic prosodic modulations:
    - Speaking Rate (Speed)
    - Pitch Offset (Hz/semitones)
    - Energy & Volume
    - Pause Multiplier
    - SSML Expression Style
    """

    @classmethod
    def modulate_speech_style(
        cls, 
        base_profile: VoiceProfile, 
        emotion: Optional[ContinuousEmotionVector] = None
    ) -> SpeechStyleParameters:
        if emotion is None:
            emotion = ContinuousEmotionVector(valence=0.5, arousal=0.5, warmth=0.8, intensity=0.5)

        # Baseline start from profile
        rate = base_profile.speaking_rate
        pitch = base_profile.pitch_offset
        energy = base_profile.energy
        warmth = base_profile.warmth
        volume_gain = 0.0
        pause_mult = 1.0
        ssml_style = "chat"

        # 1. High Valence & High Arousal (Joy, Excitement)
        if emotion.valence >= 0.4 and emotion.arousal >= 0.4:
            rate = round(min(1.4, base_profile.speaking_rate * (1.0 + 0.15 * emotion.arousal)), 2)
            pitch = round(min(4.0, base_profile.pitch_offset + 2.0 * emotion.valence), 2)
            energy = round(min(1.0, base_profile.energy + 0.25 * emotion.arousal), 2)
            warmth = round(min(1.0, base_profile.warmth + 0.2 * emotion.warmth), 2)
            volume_gain = round(1.5 * emotion.arousal, 1)
            pause_mult = 0.85
            ssml_style = "cheerful"

        # 2. Low Valence & Low Arousal (Sadness, Grief, Heavy Concern)
        elif emotion.valence <= -0.3 and emotion.arousal <= 0.4:
            rate = round(max(0.75, base_profile.speaking_rate * (1.0 - 0.20 * emotion.intensity)), 2)
            pitch = round(max(-3.0, base_profile.pitch_offset - 1.5 * emotion.intensity), 2)
            energy = round(max(0.2, base_profile.energy - 0.3 * emotion.intensity), 2)
            warmth = round(min(1.0, base_profile.warmth + 0.25 * emotion.warmth), 2)
            volume_gain = -2.0
            pause_mult = 1.4
            ssml_style = "empathetic"

        # 3. High Warmth & Moderate Valence (Deep Empathy, Comfort, Listening)
        elif emotion.warmth >= 0.7:
            rate = round(max(0.9, base_profile.speaking_rate * 0.95), 2)
            pitch = round(base_profile.pitch_offset + 0.5, 2)
            energy = round(base_profile.energy * 0.9, 2)
            warmth = round(min(1.0, emotion.warmth), 2)
            volume_gain = 0.0
            pause_mult = 1.15
            ssml_style = "warm"

        # 4. High Arousal & Negative Valence (Urgency, Surprise, Worry)
        elif emotion.arousal >= 0.6 and emotion.valence < 0.0:
            rate = round(min(1.3, base_profile.speaking_rate * 1.15), 2)
            pitch = round(min(3.5, base_profile.pitch_offset + 1.5), 2)
            energy = round(min(1.0, base_profile.energy + 0.3), 2)
            volume_gain = 1.0
            pause_mult = 0.8
            ssml_style = "serious"

        return SpeechStyleParameters(
            speaking_rate=rate,
            pitch_offset=pitch,
            volume_gain_db=volume_gain,
            energy=energy,
            warmth=warmth,
            pause_multiplier=pause_mult,
            ssml_style=ssml_style
        )
