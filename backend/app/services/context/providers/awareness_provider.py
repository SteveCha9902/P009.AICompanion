from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.awareness.awareness_context import AwarenessContext
from app.services.awareness.reaction_planner import AwarenessReactionPlanner

class AwarenessContextProvider(ContextProvider):
    """
    4th Cognitive Layer: Visual Awareness & Companion Perception Provider.
    Injects fresh, non-intrusive visual hints into ContextBuilder prompt.
    """

    def __init__(self, awareness_context: Optional[AwarenessContext] = None):
        self.awareness_context = awareness_context

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        if not self.awareness_context:
            return []
        guidance = AwarenessReactionPlanner.build_awareness_prompt_guidance(self.awareness_context)
        if not guidance:
            return []
        return [{"role": "system", "content": guidance}]
