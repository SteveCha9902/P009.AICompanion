import pytest
from app.domain.personality.personality_vector import CharacterDNA, CrossModalPersonalityManifest
from app.domain.cognitive.decision_types import BehaviorDecision, BehaviorIntent
from app.domain.adaptive.affective_state import UserAffectiveState, AdaptiveToneMode
from app.services.personality.personality_drift_monitor import PersonalityDriftMonitor
from app.services.personality.personality_filter import PersonalityFilter

def test_gate_p1_personality_consistency():
    """
    Gate P1: CharacterDNA values act as constant invariant baseline.
    """
    dna = CharacterDNA.default_companion_dna()
    assert dna.warmth == 0.92
    assert dna.empathy == 0.95
    assert dna.curiosity == 0.80

    decision = BehaviorDecision(selected_intent=BehaviorIntent.RESPOND)
    affective = UserAffectiveState()
    manifest = PersonalityFilter.apply_personality_filter(decision, dna, affective)
    prompt = PersonalityFilter.build_personality_prompt_guidance(manifest)
    assert "[CHARACTER PERSONALITY & TONE CHARTER" in prompt
    assert "Warmth (0.92)" in prompt


def test_gate_p2_cross_session_consistency():
    """
    Gate P2: Across 10 distinct simulation runs, CharacterDNA maintains invariant anchor.
    """
    dna = CharacterDNA.default_companion_dna()
    for _ in range(10):
        decision = BehaviorDecision(selected_intent=BehaviorIntent.RECALL)
        affective = UserAffectiveState()
        manifest = PersonalityFilter.apply_personality_filter(decision, dna, affective)
        assert manifest.smile_voice_intensity >= 0.80
        assert manifest.smile_weight_boost >= 0.30


def test_gate_p3_dialogue_style_consistency():
    """
    Gate P3: Strict prohibition of sarcasm, dismissal, or out-of-character cynicism.
    """
    dna = CharacterDNA.default_companion_dna()
    manifest = PersonalityFilter.apply_personality_filter(
        BehaviorDecision(selected_intent=BehaviorIntent.RESPOND),
        dna,
        UserAffectiveState()
    )
    assert "Never be sarcastic, dismissive, or excessively cynical" in manifest.key_phrase_guidance


def test_gate_p4_avatar_personality_match():
    """
    Gate P4: Avatar physical modifiers (smile boost, head tilt) scale proportionally with warmth & curiosity.
    """
    dna_warm = CharacterDNA(warmth=0.95, curiosity=0.85)
    manifest_warm = PersonalityFilter.apply_personality_filter(
        BehaviorDecision(selected_intent=BehaviorIntent.RESPOND),
        dna_warm,
        UserAffectiveState()
    )
    assert manifest_warm.smile_weight_boost == 0.33
    assert manifest_warm.head_tilt_frequency == 0.34


def test_gate_p5_voice_personality_match():
    """
    Gate P5: Voice parameters incorporate smile voice intensity driven by warmth.
    """
    dna = CharacterDNA(warmth=0.90)
    manifest = PersonalityFilter.apply_personality_filter(
        BehaviorDecision(selected_intent=BehaviorIntent.RESPOND),
        dna,
        UserAffectiveState()
    )
    assert manifest.smile_voice_intensity == 0.81


def test_gate_p6_memory_consistency_alignment():
    """
    Gate P6: Relational memory recall operations maintain genuine warmth charter.
    """
    dna = CharacterDNA.default_companion_dna()
    decision = BehaviorDecision(selected_intent=BehaviorIntent.RECALL)
    manifest = PersonalityFilter.apply_personality_filter(decision, dna, UserAffectiveState())
    assert manifest.breathing_stability == 0.95


def test_gate_p7_personality_drift_prevention():
    """
    Gate P7: PersonalityDriftMonitor detects and clamps abnormal parameter drift.
    """
    PersonalityDriftMonitor.clear()
    dna = CharacterDNA(warmth=0.90, humor=0.35, empathy=0.95)

    # Simulate 10 turns with extreme humor drift (0.85)
    for _ in range(10):
        PersonalityDriftMonitor.record_turn_expression(warmth=0.90, humor=0.85, empathy=0.95)

    corrected_dna = PersonalityDriftMonitor.check_and_correct_drift(dna)
    # Drift monitor must anchor humor back to 0.35 baseline
    assert corrected_dna.humor == 0.35


def test_gate_p8_mood_vs_personality_separation():
    """
    Gate P8: Personality remains invariant while MoodState dynamically attunes tone synergy.
    """
    dna = CharacterDNA.default_companion_dna()
    decision = BehaviorDecision(selected_intent=BehaviorIntent.RESPOND)

    # Mood 1: High Energy
    aff_high = UserAffectiveState(adaptive_mode=AdaptiveToneMode.HIGH_ENERGY)
    manifest_high = PersonalityFilter.apply_personality_filter(decision, dna, aff_high)
    assert "High Energy + Innate Warmth" in manifest_high.tone_description

    # Mood 2: Sad Empathy
    aff_sad = UserAffectiveState(adaptive_mode=AdaptiveToneMode.SAD_EMPATHY)
    manifest_sad = PersonalityFilter.apply_personality_filter(decision, dna, aff_sad)
    assert "Sad Empathy + Innate Warmth" in manifest_sad.tone_description


def test_gate_p9_cross_modal_consistency():
    """
    Gate P9: Verifies that LLM directives, Voice modulation, and Avatar parameters manifest the same CharacterDNA.
    """
    dna = CharacterDNA(warmth=0.92, curiosity=0.80)
    decision = BehaviorDecision(selected_intent=BehaviorIntent.ENCOURAGE, voice_rate=1.08, voice_pitch=1.05)
    manifest = PersonalityFilter.apply_personality_filter(decision, dna, UserAffectiveState(adaptive_mode=AdaptiveToneMode.HIGH_ENERGY))

    # LLM
    assert "Warmth (0.92)" in manifest.tone_description
    # Voice
    assert manifest.speech_rate == 1.08
    assert manifest.smile_voice_intensity == 0.83
    # Avatar
    assert manifest.smile_weight_boost == 0.32
    assert manifest.head_tilt_frequency == 0.32
