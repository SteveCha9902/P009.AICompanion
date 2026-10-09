import time
from typing import Dict, Tuple, Optional
from app.services.character.agency.domain import AgencyActionType, DeliveryChannel

class InitiativeBudgetManager:
    """
    Manages daily initiative budgets, cooldowns, and frequency caps to prevent AI outreach spam.
    """

    ACTION_COSTS: Dict[AgencyActionType, float] = {
        AgencyActionType.STAY_SILENT: 0.0,
        AgencyActionType.INTERNAL_REFLECTION: 0.0,
        AgencyActionType.QUIET_PRESENCE: 0.05,
        AgencyActionType.GREETING: 0.10,
        AgencyActionType.FOLLOW_UP: 0.20,
        AgencyActionType.CHECK_IN: 0.20,
        AgencyActionType.OFFER_SUPPORT: 0.20,
        AgencyActionType.SHARE_MEMORY: 0.25,
        AgencyActionType.CELEBRATE: 0.20,
        AgencyActionType.OUTREACH_CANDIDATE: 0.40,
    }

    # Cooldown seconds
    NOTIFICATION_COOLDOWN_SEC = 6 * 3600 # 6 hours
    MESSAGE_COOLDOWN_SEC = 1 * 3600      # 1 hour
    SAME_ACTION_COOLDOWN_SEC = 30 * 60   # 30 mins

    def __init__(self, daily_budget: float = 1.0):
        self.daily_budget = daily_budget
        self._user_budgets: Dict[str, float] = {}
        self._last_action_times: Dict[str, float] = {}
        self._last_notification_times: Dict[str, float] = {}
        self._last_specific_action_times: Dict[Tuple[str, str], float] = {}

    def get_remaining_budget(self, user_id: str) -> float:
        return self._user_budgets.get(user_id, self.daily_budget)

    def check_eligibility(
        self,
        user_id: str,
        action_type: AgencyActionType,
        delivery_channel: DeliveryChannel,
        now_ts: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        now = now_ts or time.time()
        cost = self.ACTION_COSTS.get(action_type, 0.20)
        rem_budget = self.get_remaining_budget(user_id)

        # 1. Budget Check
        if rem_budget < cost:
            return False, "BLOCKED_BY_BUDGET"

        # 2. Notification Cooldown Check
        if delivery_channel == DeliveryChannel.NOTIFICATION:
            last_notif = self._last_notification_times.get(user_id, 0.0)
            if (now - last_notif) < self.NOTIFICATION_COOLDOWN_SEC:
                return False, "BLOCKED_BY_COOLDOWN"

        # 3. Proactive Message Cooldown Check
        if delivery_channel == DeliveryChannel.PROACTIVE_MESSAGE:
            last_act = self._last_action_times.get(user_id, 0.0)
            if (now - last_act) < self.MESSAGE_COOLDOWN_SEC:
                return False, "BLOCKED_BY_COOLDOWN"

        # 4. Same Action Type Cooldown Check
        last_same = self._last_specific_action_times.get((user_id, action_type.value), 0.0)
        if (now - last_same) < self.SAME_ACTION_COOLDOWN_SEC:
            return False, "BLOCKED_BY_COOLDOWN"

        return True, None

    def deduct_and_record(
        self,
        user_id: str,
        action_type: AgencyActionType,
        delivery_channel: DeliveryChannel,
        now_ts: Optional[float] = None
    ) -> float:
        now = now_ts or time.time()
        cost = self.ACTION_COSTS.get(action_type, 0.20)
        rem = self.get_remaining_budget(user_id)
        new_budget = max(0.0, round(rem - cost, 2))
        self._user_budgets[user_id] = new_budget

        self._last_action_times[user_id] = now
        self._last_specific_action_times[(user_id, action_type.value)] = now

        if delivery_channel == DeliveryChannel.NOTIFICATION:
            self._last_notification_times[user_id] = now

        return new_budget
