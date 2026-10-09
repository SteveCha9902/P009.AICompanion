from app.domain.adaptive.affective_state import (
    UserAffectiveState,
    AdaptiveToneMode,
    AdaptiveVoiceParameters
)
from app.services.adaptive.affective_smoother import AffectiveStateSmoother

class AdaptiveBehaviorPlanner:
    """
    Plans companion's dynamic tone, dialogue guidelines, avatar behavior modulation,
    and TTS voice modulation according to UserAffectiveState.
    """

    @classmethod
    def plan_behavior(cls, raw_state: UserAffectiveState, apply_smoothing: bool = False) -> UserAffectiveState:
        # 1. Optionally apply EMA Smoothing
        state = AffectiveStateSmoother.smooth_state(raw_state) if apply_smoothing else raw_state.model_copy()

        # 2. Confidence-First Guard: If confidence < 0.70, fallback to safe CALM mode
        if state.confidence < UserAffectiveState.MIN_EMPATHY_CONFIDENCE_THRESHOLD:
            state.adaptive_mode = AdaptiveToneMode.CALM
            state.voice_params = AdaptiveVoiceParameters(rate_modifier=0.95, pitch_modifier=1.00, style="calm")
            return state

        # 3. Adaptive Silence Guard: If receptiveness < 0.25, enter FOCUSED_SILENCE
        if state.receptiveness < UserAffectiveState.ADAPTIVE_SILENCE_THRESHOLD:
            state.adaptive_mode = AdaptiveToneMode.FOCUSED_SILENCE
            state.voice_params = AdaptiveVoiceParameters(rate_modifier=0.95, pitch_modifier=0.98, style="whisper")
            return state

        # 4. Mode determination based on Affective Dimensions
        if state.emotional_valence > 0.35 and state.energy_level > 0.60:
            mode = AdaptiveToneMode.HIGH_ENERGY
            voice = AdaptiveVoiceParameters(rate_modifier=1.08, pitch_modifier=1.05, style="cheerful")
        elif state.stress_level > 0.50:
            mode = AdaptiveToneMode.STRESSED
            voice = AdaptiveVoiceParameters(rate_modifier=0.95, pitch_modifier=0.98, style="soothing")
        elif state.emotional_valence < -0.30:
            mode = AdaptiveToneMode.SAD_EMPATHY
            voice = AdaptiveVoiceParameters(rate_modifier=0.90, pitch_modifier=0.98, style="empathetic")
        else:
            mode = AdaptiveToneMode.CALM
            voice = AdaptiveVoiceParameters(rate_modifier=0.95, pitch_modifier=1.00, style="calm")

        state.adaptive_mode = mode
        state.voice_params = voice
        return state

    @classmethod
    def build_prompt_guidance(cls, state: UserAffectiveState) -> str:
        mode = state.adaptive_mode

        if mode == AdaptiveToneMode.FOCUSED_SILENCE:
            return (
                "\n[EMOTIONAL ADAPTATION: FOCUSED SILENCE MODE]\n"
                "User is deeply focused or has very low conversational receptiveness. "
                "Keep response minimal, concise, and non-intrusive. DO NOT ask new questions or initiate long chat.\n"
            )
        elif mode == AdaptiveToneMode.HIGH_ENERGY:
            return (
                "\n[EMOTIONAL ADAPTATION: HIGH ENERGY & CHEERFUL MODE]\n"
                "User is in high spirits and energetic. "
                "Respond with bright, enthusiastic, and lively energy. Share in their joy with warm excitement.\n"
            )
        elif mode == AdaptiveToneMode.STRESSED:
            return (
                "\n[EMOTIONAL ADAPTATION: STRESS RELIEF & CALM SUPPORT MODE]\n"
                "User appears busy, stressed, or dealing with deadlines. "
                "Be soothing, peaceful, and pressure-free. DO NOT add cognitive burden or demand detailed explanations.\n"
            )
        elif mode == AdaptiveToneMode.SAD_EMPATHY:
            return (
                "\n[EMOTIONAL ADAPTATION: WARM EMPATHY MODE (No Dogmatic Labeling)]\n"
                "User may be experiencing a low mood or difficult moment. "
                "Offer warm, tender comfort and sincere listening. "
                "DO NOT dogmatically state '너 지금 우울하네' or label them. Use soft phrases like '조금 지쳐 보이기도 해' or '내가 곁에 있어줄게'.\n"
            )
        else: # CALM
            return (
                "\n[EMOTIONAL ADAPTATION: CALM & COMFORTABLE MODE]\n"
                "Maintain a gentle, pleasant, and steady companion presence.\n"
            )
