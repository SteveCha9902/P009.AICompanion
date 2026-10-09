import pytest
from datetime import datetime, timezone, timedelta
from app.db.models.relationship import RelationshipState, RelationshipSignalType, SignalSeverity, RelationshipLevel
from app.services.relationship.policy import PolicyEngine, BehaviorPolicy
from app.services.relationship.decay import DecayEngine

def test_relationship_policy_update():
    engine = PolicyEngine()
    
    # Positive Signal (Normal Severity)
    deltas = engine.evaluate_signal(RelationshipSignalType.COMPANION_HELPED_SUCCESSFULLY, SignalSeverity.MEDIUM)
    # Based on our implementation: Trust +0.03, Reliability +0.04 * 0.5 (MEDIUM multiplier) = 0.015, 0.02
    assert 'trust' in deltas
    assert 'reliability' in deltas
    assert deltas['trust'] > 0

    # Negative Signal (CRITICAL Severity)
    deltas_critical = engine.evaluate_signal(RelationshipSignalType.COMPANION_FAILED, SignalSeverity.CRITICAL)
    # Trust -0.04, Reliability -0.05 * 2.0 (CRITICAL multiplier) = -0.08, -0.10
    assert deltas_critical['trust'] < 0
    assert deltas_critical['reliability'] < 0
    assert deltas_critical['reliability'] <= -0.10

def test_relationship_level_calculation():
    engine = PolicyEngine()
    
    # Low relationship
    state_low = RelationshipState(trust=0.1, familiarity=0.1, closeness=0.1, engagement=0.1, reliability=0.1)
    assert engine.calculate_level(state_low) == RelationshipLevel.STRANGER
    
    # High relationship (engagement doesn't heavily affect level)
    state_high = RelationshipState(trust=0.9, familiarity=0.9, closeness=0.9, engagement=0.1, reliability=0.9)
    # Score = 0.9 * 0.4 + 0.9 * 0.3 + 0.9 * 0.3 = 0.9 => TRUSTED
    assert engine.calculate_level(state_high) == RelationshipLevel.TRUSTED

def test_behavior_modifiers():
    behavior_engine = BehaviorPolicy()
    state = RelationshipState(trust=0.9, familiarity=0.9, closeness=0.9, engagement=0.1, reliability=0.9)
    
    modifiers = behavior_engine.get_behavior_modifiers(state, RelationshipLevel.TRUSTED)
    # Because engagement is low (0.1 < 0.3), it should include the engagement modifier
    assert any("less engaged recently" in mod for mod in modifiers)
    # Should include trusted modifiers
    assert any("direct, honest feedback" in mod for mod in modifiers)

def test_relationship_decay():
    engine = DecayEngine()
    now = datetime.now(timezone.utc)
    
    # Base state
    state = RelationshipState(
        trust=0.8,
        familiarity=0.8,
        closeness=0.8,
        engagement=0.8,
        reliability=0.8,
        updated_at=now - timedelta(days=10) # 10 days ago
    )
    
    decayed = engine.apply_decay(state, current_time=now)
    
    # Trust decays very slow (0.01 per 30 days => ~0.003 for 10 days)
    assert 0.79 < decayed.trust < 0.8
    # Closeness decays medium (0.02 per 10 days => 0.02)
    assert abs(decayed.closeness - 0.78) < 0.001
    # Engagement decays fast (0.05 per 3 days => ~0.166 for 10 days)
    assert abs(decayed.engagement - 0.633) < 0.01
