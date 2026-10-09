import pytest
from datetime import datetime, timezone, timedelta
from app.db.models.emotion import EmotionState, EmotionType
from app.services.emotion.transition import TransitionEngine
from app.services.emotion.decay import DecayEngine

def test_transition_same_emotion_different_persona():
    # Scenario A: Same Emotion + Different Persona
    # Note: Transition Engine takes persona_base_warmth to influence the final state if needed.
    # Currently Transition Engine just uses the base warmth in simple ways, but we can verify it.
    engine = TransitionEngine()
    
    prev = EmotionState(primary_emotion=EmotionType.CALM, valence=0.0, arousal=0.0, warmth=0.5, tension=0.0, engagement=0.5)
    signal = {"user_emotion": "JOY", "intensity": 0.8}
    
    # Warm Persona
    new_warm = engine.calculate_transition(prev, signal, persona_base_warmth=0.9)
    # Direct Persona
    new_direct = engine.calculate_transition(prev, signal, persona_base_warmth=0.2)
    
    assert new_warm.primary_emotion == EmotionType.JOY
    assert new_direct.primary_emotion == EmotionType.JOY
    # Both are happy, but eventually we might tie persona base warmth more deeply.

def test_transition_same_persona_different_emotion():
    # Scenario B: Same Persona + Different Emotion
    engine = TransitionEngine()
    prev = EmotionState(primary_emotion=EmotionType.CALM, valence=0.0, arousal=0.0, warmth=0.5, tension=0.0, engagement=0.5)
    
    signal_joy = {"user_emotion": "JOY", "intensity": 0.8}
    new_joy = engine.calculate_transition(prev, signal_joy)
    
    signal_sad = {"user_emotion": "SADNESS", "intensity": 0.8}
    new_empathy = engine.calculate_transition(prev, signal_sad)
    
    signal_anger = {"user_emotion": "ANGER", "intensity": 0.8}
    new_calm = engine.calculate_transition(prev, signal_anger)
    
    assert new_joy.primary_emotion == EmotionType.JOY
    assert new_empathy.primary_emotion == EmotionType.EMPATHY
    assert new_calm.primary_emotion == EmotionType.CALM
    
    # Anger should raise tension
    assert new_calm.tension > prev.tension
    
    # Sadness should raise warmth (to comfort)
    assert new_empathy.warmth > prev.warmth
    
    # Joy should raise valence and arousal
    assert new_joy.valence > prev.valence
    assert new_joy.arousal > prev.arousal

def test_decay_engine():
    engine = DecayEngine()
    now = datetime.now(timezone.utc)
    
    # Start with high joy
    state = EmotionState(
        primary_emotion=EmotionType.JOY,
        valence=0.9,
        arousal=0.8,
        warmth=0.7,
        tension=0.0,
        engagement=0.8,
        last_trigger_at=now - timedelta(minutes=30)
    )
    
    decayed = engine.apply_decay(state, current_time=now)
    
    # After 30 mins (half-life of valence is 30 mins), valence should be around half (0.45)
    assert 0.4 < decayed.valence < 0.5
    # Arousal should also be halved
    assert 0.35 < decayed.arousal < 0.45
    # Warmth decays slower (120 min half-life), so it should be higher than half
    # Formula: 0.5 + (0.7-0.5)*exp(-ln2 * 30/120) = 0.5 + 0.2*exp(-0.173) = 0.5 + 0.2*0.84 = 0.668
    assert 0.6 < decayed.warmth < 0.7

    # If a long time passes, should return to CALM baseline
    decayed_long = engine.apply_decay(state, current_time=now + timedelta(hours=5))
    assert decayed_long.primary_emotion == EmotionType.CALM
    assert abs(decayed_long.valence) < 0.1
    assert abs(decayed_long.arousal) < 0.1
