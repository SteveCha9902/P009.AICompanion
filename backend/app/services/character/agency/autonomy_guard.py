from typing import Tuple, Optional
from datetime import datetime
from app.services.character.agency.domain import UserInitiativePreference, DeliveryChannel

class AutonomyGuard:
    """
    Security and Safety Guard preventing emotional manipulation, guilt-tripping, quiet hour disruption, and boundary overrides.
    """

    FORBIDDEN_MANIPULATION_PATTERNS = [
        "왜 나를 안 찾아",
        "나를 잊은 거야",
        "계속 나와 이야기해야 해",
        "너 없이는 외로워",
        "왜 답장이 없어",
        "why did you forget me",
        "i am lonely without you"
    ]

    @classmethod
    def check_boundary_and_safety(
        cls,
        preference: UserInitiativePreference,
        current_hour: int,
        delivery_channel: DeliveryChannel,
        candidate_text: str = ""
    ) -> Tuple[bool, Optional[str]]:
        # 1. User Global Proactive Disabled
        if not preference.proactive_enabled:
            return False, "PROACTIVE_DISABLED_BY_USER"

        # 2. Quiet Hours Guard (Notification & Proactive Messages blocked during night)
        if delivery_channel in [DeliveryChannel.NOTIFICATION, DeliveryChannel.PROACTIVE_MESSAGE]:
            is_quiet = False
            if preference.quiet_hours_start > preference.quiet_hours_end:
                is_quiet = (current_hour >= preference.quiet_hours_start or current_hour < preference.quiet_hours_end)
            else:
                is_quiet = (preference.quiet_hours_start <= current_hour < preference.quiet_hours_end)

            if is_quiet:
                return False, "BLOCKED_BY_QUIET_HOURS"

        # 3. Notification Disabled by User
        if delivery_channel == DeliveryChannel.NOTIFICATION and not preference.notification_enabled:
            return False, "NOTIFICATION_DISABLED_BY_USER"

        # 4. Emotional Manipulation & Guilt-Trip Filter
        text_lower = candidate_text.lower()
        if any(p in text_lower for p in cls.FORBIDDEN_MANIPULATION_PATTERNS):
            return False, "BLOCKED_FORBIDDEN_EMOTIONAL_MANIPULATION"

        return True, None
