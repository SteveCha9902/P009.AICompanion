from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.services.character.agency.domain import InitiativeDecision, DeliveryChannel, DecisionStatus

class ActionScheduler:
    """
    Schedules and dispatches valid InitiativeDecisions to their respective channels (UI Presence, Proactive Message, Notification).
    """

    @staticmethod
    def create_execution_payload(decision: InitiativeDecision) -> Dict[str, Any]:
        if not decision.should_act:
            return {
                "execute": False,
                "status": decision.decision_status.value,
                "blocked_reason": decision.blocked_reason,
                "reason": decision.reason
            }

        return {
            "execute": True,
            "action_type": decision.action_type.value,
            "channel": decision.delivery_channel.value,
            "priority": decision.priority_score,
            "scheduled_at": decision.timing.isoformat() if decision.timing else datetime.now(timezone.utc).isoformat(),
            "reason": decision.reason,
            "budget_cost": decision.budget_cost,
            "status": DecisionStatus.EXECUTED.value
        }
