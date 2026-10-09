from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.services.cognitive.cognitive_decision_engine import CognitiveDecisionEngine

class CognitiveContextProvider(ContextProvider):
    """
    Central Brain OS Context Provider:
    Injects high-level BehaviorDecision directives and Decision Trace into ContextBuilder prompt.
    """

    def __init__(self, user_id: str = "default_user", idle_seconds: float = 60.0):
        self.user_id = user_id
        self.idle_seconds = idle_seconds

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        decision = CognitiveDecisionEngine.evaluate_decision(
            user_id=self.user_id,
            user_utterance=current_user_message,
            idle_seconds=self.idle_seconds
        )

        if not decision.prompt_directive:
            return []

        return [{
            "role": "system",
            "content": f"\n[COMPANION COGNITIVE OS (CCOS) DECISION]\nIntent: {decision.selected_intent.value} (Confidence: {decision.confidence:.2f})\nTrace: {decision.trace_reason}\n{decision.prompt_directive}"
        }]
