from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.shared_reality.shared_reality_context import SharedRealityContext
from app.services.shared_reality.shared_reality_planner import SharedRealityPlanner
from app.services.shared_reality.joint_attention_engine import JointAttentionEngine

class SharedRealityContextProvider(ContextProvider):
    """
    Cognitive Layer: Shared Reality & Joint Attention Context Provider.
    Injects joint visual focus directives into ContextBuilder prompt.
    """

    def __init__(self, shared_reality_context: Optional[SharedRealityContext] = None):
        self.shared_reality_context = shared_reality_context

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        ctx = self.shared_reality_context or JointAttentionEngine.get_active_context()
        if not ctx:
            return []
        directive = SharedRealityPlanner.build_shared_reality_directive(ctx)
        if not directive:
            return []
        return [{"role": "system", "content": directive}]
