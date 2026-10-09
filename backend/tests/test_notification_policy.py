import pytest
from datetime import datetime, timezone, timedelta
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.db.models.notification import NotificationSettings
from app.services.notifications.policy import NotificationPolicyEngine

def test_notification_policy_engine_never_disturb():
    engine = NotificationPolicyEngine()
    presence = PresenceState(state=PresenceStateEnum.IDLE)
    settings = NotificationSettings(notifications_enabled=True, never_disturb=True)
    
    should_push, reason = engine.evaluate(presence, settings)
    assert should_push == False
    assert "Never Disturb" in reason

def test_notification_policy_engine_disabled():
    engine = NotificationPolicyEngine()
    presence = PresenceState(state=PresenceStateEnum.IDLE)
    settings = NotificationSettings(notifications_enabled=False, never_disturb=False)
    
    should_push, reason = engine.evaluate(presence, settings)
    assert should_push == False
    assert "disabled" in reason

def test_notification_policy_engine_in_app_delivery():
    engine = NotificationPolicyEngine()
    now = datetime.now(timezone.utc)
    # User just active 1 min ago
    presence = PresenceState(
        state=PresenceStateEnum.AVAILABLE, 
        last_active_at=now - timedelta(minutes=1)
    )
    # 00:00 to 00:00 means quiet hours are effectively off for this test
    settings = NotificationSettings(
        notifications_enabled=True, 
        never_disturb=False,
        quiet_hours_start="00:00",
        quiet_hours_end="00:00"
    )
    
    should_push, reason = engine.evaluate(presence, settings)
    assert should_push == False
    assert "In-App Delivery" in reason

def test_notification_policy_engine_allow_push():
    engine = NotificationPolicyEngine()
    now = datetime.now(timezone.utc)
    # User active 10 mins ago -> should send push
    presence = PresenceState(
        state=PresenceStateEnum.AVAILABLE, 
        last_active_at=now - timedelta(minutes=10)
    )
    settings = NotificationSettings(
        notifications_enabled=True, 
        never_disturb=False,
        quiet_hours_start="00:00",
        quiet_hours_end="00:00"
    )
    
    should_push, reason = engine.evaluate(presence, settings)
    assert should_push == True
