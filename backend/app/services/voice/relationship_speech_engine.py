from typing import Optional
from app.domain.voice.voice_profile import SpeechStyleParameters
from app.domain.relationship.relationship_stage import RelationshipStage
from app.services.character.avatar.domain import RelationshipParameters

class RelationshipSpeechEngine:
    """
    Modulates speech prosody and honorifics based on Relationship Stage & Social Bond:
    - Stranger: Polished, respectful, clear articulation, formal cadence
    - Acquaintance: Friendly, approachable, moderate warmth
    - Close Friend: Relaxed rhythm, higher playfulness, colloquial pauses
    - Trusted Companion: Intimate softness, deep emotional resonance, gentle cadence
    """

    @classmethod
    def apply_relationship_modulation(
        cls,
        style: SpeechStyleParameters,
        stage: RelationshipStage = RelationshipStage.ACQUAINTANCE,
        rel_params: Optional[RelationshipParameters] = None
    ) -> SpeechStyleParameters:
        
        warmth_bias = rel_params.warmth if rel_params else 0.5
        trust_bias = rel_params.trust if rel_params else 0.5

        if stage == RelationshipStage.STRANGER:
            # Respectful, crisp, slight distance
            style.speaking_rate = round(style.speaking_rate * 0.98, 2)
            style.pitch_offset = round(style.pitch_offset * 0.9, 2)
            style.pause_multiplier = round(style.pause_multiplier * 1.1, 2)
            style.warmth = round(min(0.6, style.warmth), 2)
            style.ssml_style = "formal"

        elif stage == RelationshipStage.ACQUAINTANCE:
            # Polite, bright, friendly
            style.warmth = round(max(0.65, style.warmth), 2)
            style.ssml_style = "friendly"

        elif stage == RelationshipStage.FRIEND or stage == RelationshipStage.CLOSE_FRIEND:
            # Comfortable, expressive, playful
            style.speaking_rate = round(style.speaking_rate * 1.03, 2)
            style.warmth = round(min(1.0, max(0.8, style.warmth + warmth_bias * 0.15)), 2)
            style.energy = round(min(1.0, style.energy + 0.05), 2)
            style.pause_multiplier = round(style.pause_multiplier * 0.95, 2)
            style.ssml_style = "cheerful" if style.energy >= 0.7 else "chat"

        elif stage == RelationshipStage.TRUSTED_COMPANION:
            # Soft, intimate, highly empathetic, relaxed breathing pauses
            style.speaking_rate = round(style.speaking_rate * 0.96, 2)
            style.pitch_offset = round(style.pitch_offset + 0.3, 2)
            style.warmth = round(min(1.0, 0.90 + warmth_bias * 0.10), 2)
            style.pause_multiplier = round(style.pause_multiplier * 1.15, 2)
            style.ssml_style = "warm"

        return style
