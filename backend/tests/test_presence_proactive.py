import pytest
from datetime import datetime, timezone, timedelta
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.db.models.proactive import ProactiveSettings, ProactiveTriggerType, ProactiveDecision
from app.db.models.relationship import RelationshipState, RelationshipLevel
from app.services.proactive_service import ProactivePolicyEngine

@pytest.mark.asyncio
async def test_proactive_policy_quiet_hours():
    class MockRepo:
        async def get_settings(self, companion_id: str):
            return ProactiveSettings(
                enabled=True,
                quiet_hours_start="23:00",
                quiet_hours_end="07:00",
                daily_limit=3,
                cooldown_minutes=60
            )
        async def get_recent_events(self, companion_id: str, limit: int):
            return []

    engine = ProactivePolicyEngine(MockRepo())
    
    # Check quiet hours method directly
    # 23:30 should be in quiet hours
    assert engine._is_quiet_hours("23:30", "23:00", "07:00") == True
    # 02:00 should be in quiet hours
    assert engine._is_quiet_hours("02:00", "23:00", "07:00") == True
    # 12:00 should NOT be in quiet hours
    assert engine._is_quiet_hours("12:00", "23:00", "07:00") == False
    
    # Check 09:00 - 18:00 logic
    assert engine._is_quiet_hours("12:00", "09:00", "18:00") == True
    assert engine._is_quiet_hours("20:00", "09:00", "18:00") == False

@pytest.mark.asyncio
async def test_proactive_policy_stranger_denial():
    class MockRepo:
        async def get_settings(self, companion_id: str):
            return ProactiveSettings(enabled=True, daily_limit=5, cooldown_minutes=0, quiet_hours_start="00:00", quiet_hours_end="00:00")
        async def get_recent_events(self, companion_id: str, limit: int):
            return []

    engine = ProactivePolicyEngine(MockRepo())
    
    presence = PresenceState(state=PresenceStateEnum.AVAILABLE)
    # STRANGER relationship
    relationship = RelationshipState(relationship_level=RelationshipLevel.STRANGER)
    
    # Try TIME_BASED trigger on stranger -> should DENY
    decision, score, reason = await engine.evaluate_eligibility(
        "test_c_id", presence, relationship, ProactiveTriggerType.TIME_BASED
    )
    
    assert decision == ProactiveDecision.DENY
    assert "STRANGER" in reason
    
@pytest.mark.asyncio
async def test_proactive_policy_long_absence_allow():
    class MockRepo:
        async def get_settings(self, companion_id: str):
            return ProactiveSettings(enabled=True, daily_limit=5, cooldown_minutes=0, quiet_hours_start="23:00", quiet_hours_end="23:01")
        async def get_recent_events(self, companion_id: str, limit: int):
            return []

    engine = ProactivePolicyEngine(MockRepo())
    
    # 5 days absence
    last_int = datetime.now(timezone.utc) - timedelta(days=5)
    presence = PresenceState(state=PresenceStateEnum.IDLE, last_interaction_at=last_int)
    
    # CLOSE relationship
    relationship = RelationshipState(relationship_level=RelationshipLevel.CLOSE)
    
    # Should ALLOW
    decision, score, reason = await engine.evaluate_eligibility(
        "test_c_id", presence, relationship, ProactiveTriggerType.LONG_ABSENCE, memory_context_count=2
    )
    
    assert decision == ProactiveDecision.ALLOW
    assert score >= 0.6
