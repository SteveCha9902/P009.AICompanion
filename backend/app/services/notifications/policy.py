from typing import Dict, Any, Tuple
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.db.models.notification import NotificationSettings
from datetime import datetime, timezone

class NotificationPolicyEngine:
    def evaluate(self, presence: PresenceState, settings: NotificationSettings) -> Tuple[bool, str]:
        """
        Returns (Should Push?, Reason)
        """
        if not settings.notifications_enabled:
            return False, "User disabled all notifications."

        if settings.never_disturb:
            return False, "User has 'Never Disturb' active."

        # Quiet Hours Check
        now = datetime.now(timezone.utc)
        current_time_str = now.strftime("%H:%M")
        
        # We reuse the logic from Proactive Engine or duplicate it simply
        start = settings.quiet_hours_start if hasattr(settings, 'quiet_hours_start') else "23:00"
        end = settings.quiet_hours_end if hasattr(settings, 'quiet_hours_end') else "07:00"
        
        in_quiet_hours = False
        if start > end:
            in_quiet_hours = current_time_str >= start or current_time_str <= end
        else:
            in_quiet_hours = start <= current_time_str <= end
            
        if in_quiet_hours:
            return False, "Currently in quiet hours."

        # App Lifecycle check (mapped to Presence)
        # If the app is active, we don't send a push notification, we rely on In-App delivery.
        if presence.state in (PresenceStateEnum.ENGAGED, PresenceStateEnum.AVAILABLE):
            # Caution: in our system AVAILABLE might mean app is foreground OR background but listening.
            # In Sprint 8, if they are active within the last 3 minutes, we assume In-App.
            if presence.last_active_at:
                minutes_since_active = (now - presence.last_active_at.replace(tzinfo=timezone.utc)).total_seconds() / 60
                if minutes_since_active < 3:
                    return False, "User is currently active (In-App Delivery)."

        return True, "Passed all policies."
