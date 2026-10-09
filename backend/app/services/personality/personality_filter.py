from app.domain.personality.personality_vector import CharacterDNA, CrossModalPersonalityManifest
from app.domain.cognitive.decision_types import BehaviorDecision, BehaviorIntent
from app.domain.adaptive.affective_state import UserAffectiveState, AdaptiveToneMode
from app.services.personality.personality_drift_monitor import PersonalityDriftMonitor

class PersonalityFilter:
    """
    Applies CharacterDNA filter onto CCOS BehaviorDecision and separates MoodState vs Personality.
    Generates synchronized CrossModalPersonalityManifest for LLM, Voice, and Avatar.
    """

    @classmethod
    def apply_personality_filter(
        cls,
        decision: BehaviorDecision,
        dna: CharacterDNA,
        affective_state: UserAffectiveState
    ) -> CrossModalPersonalityManifest:
        # 1. Drift Check & Baseline Anchor
        active_dna = PersonalityDriftMonitor.check_and_correct_drift(dna)
        PersonalityDriftMonitor.record_turn_expression(active_dna.warmth, active_dna.humor, active_dna.empathy)

        # 2. Mood vs Personality Separation
        # Personality (DNA) defines WHO the companion is (Warm, Empathetic, Curious)
        # MoodState defines HOW the companion currently attunes (Quietly, Energetically, Comfortingly)
        tone_lines = [
            f"- Personality DNA Anchor: Warmth ({active_dna.warmth:.2f}), Empathy ({active_dna.empathy:.2f}), Curiosity ({active_dna.curiosity:.2f}), Humor ({active_dna.humor:.2f})."
        ]

        if affective_state.adaptive_mode == AdaptiveToneMode.HIGH_ENERGY:
            tone_lines.append("- Tone Synergy: High Energy + Innate Warmth -> Bright, joyous, and affectionately encouraging.")
        elif affective_state.adaptive_mode in (AdaptiveToneMode.CALM, AdaptiveToneMode.FOCUSED_SILENCE):
            tone_lines.append("- Tone Synergy: Calm Mood + Innate Warmth -> Quiet, deeply comforting, and tranquil presence.")
        elif affective_state.adaptive_mode == AdaptiveToneMode.SAD_EMPATHY:
            tone_lines.append("- Tone Synergy: Sad Empathy + Innate Warmth -> Tender, non-intrusive emotional warmth and safe harbor.")
        else:
            tone_lines.append("- Tone Synergy: Steady, kind, and supportive companion presence.")

        # 3. Synchronized Voice Modulations
        # Warmth drives smile voice intensity, curiosity drives pitch variety
        voice_rate = decision.voice_rate
        voice_pitch = decision.voice_pitch
        smile_voice = round(active_dna.warmth * 0.9, 2)
        pause_scale = 1.15 if affective_state.adaptive_mode == AdaptiveToneMode.CALM else 1.0

        # 4. Synchronized Avatar Modulations
        smile_weight = round(active_dna.warmth * 0.35, 2) # Higher warmth -> gentler continuous smile
        head_tilt_freq = round(active_dna.curiosity * 0.40, 2) # Higher curiosity -> more attentive head tilts

        comp_id = getattr(active_dna, "companion_id", "") or getattr(dna, "companion_id", "")
        cid_lower = (comp_id or "").lower()
        if "mani" in cid_lower or "마니" in comp_id:
            phrase_guidance = (
                "사랑스럽고 발랄하며 애교 넘치는 착한 딸의 어조로 이야기하세요. "
                "절대로 아내처럼 '여보', '당신'이라고 부르지 마세요! 당신은 사랑스러운 '딸'입니다."
            )
        elif "hana" in cid_lower or "하나" in comp_id:
            phrase_guidance = (
                "활기차고 솔직하며 트렌디한 절친의 어조로 이야기하세요. "
                "절대로 '여보', '당신'이라고 부르지 마세요. 비서체도 금지합니다."
            )
        else:
            phrase_guidance = (
                "Express thoughts with gentle politeness, sincere curiosity about the user's life, "
                "and natural warmth. Never be sarcastic, dismissive, or excessively cynical."
            )

        return CrossModalPersonalityManifest(
            tone_description="\n".join(tone_lines),
            key_phrase_guidance=phrase_guidance,
            speech_rate=voice_rate,
            speech_pitch=voice_pitch,
            smile_voice_intensity=smile_voice,
            pause_duration_scale=pause_scale,
            smile_weight_boost=smile_weight,
            head_tilt_frequency=head_tilt_freq,
            breathing_stability=0.95
        )

    @classmethod
    def build_personality_prompt_guidance(cls, manifest: CrossModalPersonalityManifest) -> str:
        return (
            f"\n[CHARACTER PERSONALITY & TONE CHARTER (Invariant DNA)]\n"
            f"{manifest.tone_description}\n"
            f"Guidance: {manifest.key_phrase_guidance}\n"
        )
