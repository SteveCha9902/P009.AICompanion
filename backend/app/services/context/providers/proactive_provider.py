from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.proactive.proactive_context import ProactiveOpportunity
from app.services.proactive.opportunity_detector import ProactiveOpportunityDetector
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator

class ProactiveContextProvider(ContextProvider):
    """
    Cognitive Layer: Proactive Companion Provider.
    Injects gentle, timely proactive starter prompts when opportune.
    """

    def __init__(self, user_id: str = "default_user", idle_seconds: float = 60.0):
        self.user_id = user_id
        self.idle_seconds = idle_seconds

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        opportunity = ProactiveOpportunityDetector.detect_best_proactive_opportunity(
            user_id=self.user_id,
            last_user_message=current_user_message,
            awareness_context=awareness_ctx,
            idle_seconds=self.idle_seconds
        )

        if not opportunity:
            return []

        directive = (
            f"\n[PROACTIVE COMPANION DIRECTIVE (Gentle Life Follow-up)]\n"
            f"Trigger: {opportunity.trigger_type.value} | Topic: {opportunity.topic} | Style: {opportunity.dialogue_style.value}\n"
            f"Suggested Starter Inspiration: '{opportunity.suggested_starter}'\n"
            f"Guidelines: Bring up this topic warmly and naturally. DO NOT sound like a manager checking on progress or interrogating ('왜 안 했어?'). Keep it light, empathetic, and encouraging.\n"
        )

        return [{"role": "system", "content": directive}]
