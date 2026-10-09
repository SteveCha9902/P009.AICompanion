from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.adaptive.affective_state import UserAffectiveState, AdaptiveToneMode
from app.services.autonomy.autonomy_budget_manager import AutonomyBudgetManager
from app.services.autonomy.interruption_detector import InterruptionDetector

class AutonomyPolicy:
    """
    Hard Safety & Ethical Guardrails for Companion Autonomy.
    Enforces 'User Comfort First' and strict boundaries against manipulation or over-chattiness.
    """

    @classmethod
    def apply_comfort_filter(
        cls,
        proposed_intent: BehaviorIntent,
        user_utterance: str,
        affective_state: UserAffectiveState
    ) -> BehaviorIntent:
        # Rule 1: Extreme fatigue / low receptiveness -> SILENT_COMPANION
        if affective_state.receptiveness < 0.25 or affective_state.adaptive_mode == AdaptiveToneMode.FOCUSED_SILENCE:
            return BehaviorIntent.SILENT_COMPANION

        # Rule 2: Interruption detection -> WAIT or SILENT_COMPANION
        if InterruptionDetector.should_suppress_interruption(user_utterance, None, affective_state):
            return BehaviorIntent.WAIT

        # Rule 3: Proactive speech budget exhausted
        if proposed_intent in (BehaviorIntent.PROACTIVE_START, BehaviorIntent.GENTLE_RECALL):
            if not AutonomyBudgetManager.can_initiate_autonomous_speech():
                return BehaviorIntent.LIGHT_ATTENTION

        return proposed_intent
