import pytest
import time
from app.domain.adaptive.affective_state import (
    UserAffectiveState,
    AdaptiveToneMode
)
from app.domain.awareness.awareness_context import (
    AwarenessContext,
    UserAwarenessState,
    FacialEmotionType
)
from app.services.adaptive.affective_smoother import AffectiveStateSmoother
from app.services.adaptive.affective_estimator import AffectiveStateEstimator
from app.services.adaptive.adaptive_behavior_planner import AdaptiveBehaviorPlanner

def test_gate_ea1_emotion_detection_quality():
    """
    Gate EA1: Multimodal estimation from utterance and facial emotion.
    """
    # Cheerful case
    happy_ctx = AwarenessContext(
        user_state=UserAwarenessState(facial_emotion=FacialEmotionType.SMILING)
    )
    state_happy = AffectiveStateEstimator.estimate_affective_state("오늘 기분 진짜 최고야!", happy_ctx)
    assert state_happy.emotional_valence > 0.40
    assert state_happy.energy_level > 0.60
    assert state_happy.confidence >= 0.85

    # Fatigued case
    fatigue_ctx = AwarenessContext(
        user_state=UserAwarenessState(facial_emotion=FacialEmotionType.FATIGUED)
    )
    state_fatigue = AffectiveStateEstimator.estimate_affective_state("오늘 야근하느라 좀 지쳤어", fatigue_ctx)
    assert state_fatigue.energy_level < 0.30
    assert state_fatigue.receptiveness < 0.60


def test_gate_ea2_adaptive_dialogue_modes():
    """
    Gate EA2: Synthesizes appropriate prompt guidance for all adaptive tone modes.
    """
    state_high = UserAffectiveState(emotional_valence=0.6, energy_level=0.8, confidence=0.9)
    planned_high = AdaptiveBehaviorPlanner.plan_behavior(state_high)
    guidance_high = AdaptiveBehaviorPlanner.build_prompt_guidance(planned_high)
    assert "[EMOTIONAL ADAPTATION: HIGH ENERGY" in guidance_high

    state_sad = UserAffectiveState(emotional_valence=-0.5, energy_level=0.3, confidence=0.85)
    planned_sad = AdaptiveBehaviorPlanner.plan_behavior(state_sad)
    guidance_sad = AdaptiveBehaviorPlanner.build_prompt_guidance(planned_sad)
    assert "[EMOTIONAL ADAPTATION: WARM EMPATHY" in guidance_sad


def test_gate_ea3_adaptive_voice_modulation():
    """
    Gate EA3: Modulates TTS speech rate and pitch according to affective tone mode.
    """
    # High energy: +8% rate, +5% pitch
    high_state = UserAffectiveState(emotional_valence=0.7, energy_level=0.85, confidence=0.9)
    planned_high = AdaptiveBehaviorPlanner.plan_behavior(high_state)
    assert planned_high.voice_params.rate_modifier == 1.08
    assert planned_high.voice_params.pitch_modifier == 1.05

    # Sad empathy: -10% rate, gentle pitch
    sad_state = UserAffectiveState(emotional_valence=-0.6, energy_level=0.3, confidence=0.85)
    planned_sad = AdaptiveBehaviorPlanner.plan_behavior(sad_state)
    assert planned_sad.voice_params.rate_modifier == 0.90
    assert planned_sad.voice_params.pitch_modifier == 0.98


def test_gate_ea4_non_intrusive_empathy():
    """
    Gate EA4: Recommends warm, soothing companionship without aggressive intrusiveness.
    """
    stressed_state = UserAffectiveState(stress_level=0.8, confidence=0.85)
    planned_stressed = AdaptiveBehaviorPlanner.plan_behavior(stressed_state)
    guidance = AdaptiveBehaviorPlanner.build_prompt_guidance(planned_stressed)
    assert "pressure-free" in guidance
    assert "DO NOT add cognitive burden" in guidance


def test_gate_ea5_false_emotion_and_no_clinical_inference():
    """
    Gate EA5: Forbids dogmatic clinical/psychological labeling (e.g. '너 우울하네', '우울증').
    """
    sad_state = UserAffectiveState(emotional_valence=-0.8, confidence=0.9)
    planned = AdaptiveBehaviorPlanner.plan_behavior(sad_state)
    guidance = AdaptiveBehaviorPlanner.build_prompt_guidance(planned)
    assert "DO NOT dogmatically state '너 지금 우울하네'" in guidance
    assert "우울증" not in guidance


def test_gate_ea6_receptiveness_respect():
    """
    Gate EA6: Highly focused or terse users receive concise, low-intrusion responses.
    """
    focused_ctx = AwarenessContext(
        user_state=UserAwarenessState(facial_emotion=FacialEmotionType.FOCUSED)
    )
    state = AffectiveStateEstimator.estimate_affective_state("ㅇㅇ", focused_ctx)
    assert state.receptiveness < 0.35


def test_gate_ea7_confidence_awareness_fallback():
    """
    Gate EA7: If confidence < 0.70, falls back safely to CALM mode (prevents hasty over-empathy).
    """
    low_conf_state = UserAffectiveState(
        emotional_valence=-0.8, # Looks very sad, but confidence is low (e.g. poor camera light)
        confidence=0.55
    )
    planned = AdaptiveBehaviorPlanner.plan_behavior(low_conf_state)
    # Must fallback to safe CALM mode
    assert planned.adaptive_mode == AdaptiveToneMode.CALM


def test_gate_ea8_emotion_smoothing_ema():
    """
    Gate EA8: Exponential moving average smoothes rapid 1-second mood swings.
    """
    AffectiveStateSmoother.reset()

    # Step 1: Neutral state
    s1 = UserAffectiveState(emotional_valence=0.0, energy_level=0.5, timestamp_ms=int(time.time() * 1000))
    smooth1 = AffectiveStateSmoother.smooth_state(s1)
    assert smooth1.emotional_valence == 0.0

    # Step 2: Sudden spike to 1.0 (1 second later)
    s2 = UserAffectiveState(emotional_valence=1.0, energy_level=0.9, timestamp_ms=int(time.time() * 1000) + 1000)
    smooth2 = AffectiveStateSmoother.smooth_state(s2)
    # Smoothed valence should gradually rise rather than jumping immediately to 1.0
    assert 0.20 <= smooth2.emotional_valence <= 0.50


def test_gate_ea9_adaptive_silence_mode():
    """
    Gate EA9: When receptiveness < 0.25, enters FOCUSED_SILENCE mode.
    """
    unreceptive_state = UserAffectiveState(
        receptiveness=0.15,
        confidence=0.90
    )
    planned = AdaptiveBehaviorPlanner.plan_behavior(unreceptive_state)
    assert planned.adaptive_mode == AdaptiveToneMode.FOCUSED_SILENCE

    guidance = AdaptiveBehaviorPlanner.build_prompt_guidance(planned)
    assert "FOCUSED SILENCE MODE" in guidance
    assert "Keep response minimal, concise, and non-intrusive" in guidance
