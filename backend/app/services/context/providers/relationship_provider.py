from typing import List, Optional
from app.services.context.providers.base import ContextProvider
from app.services.relationship.relationship_engine import RelationshipEngine
from app.services.relationship.relationship_context_compiler import RelationshipContextCompiler
from app.services.relationship.relationship_anchor_service import RelationshipAnchorService
import logging

logger = logging.getLogger(__name__)

class RelationshipContextProvider(ContextProvider):
    def __init__(self, relationship_service=None, companion_repo=None, user_id: str = "default_user", db=None, companion_id: str = "default_companion"):
        self.relationship_service = relationship_service
        self.companion_repo = companion_repo
        self.user_id = user_id
        self.db = db
        self.companion_id = companion_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        try:
            companion_id = getattr(self, "companion_id", "default_companion")
            if not companion_id or companion_id == "default_companion":
                if self.companion_repo:
                    try:
                        companion = await self.companion_repo.get_by_user_id(self.user_id)
                        if companion:
                            companion_id = companion.id
                    except Exception:
                        pass

            # 1. Use DB Engine if available
            if self.db:
                engine = RelationshipEngine(self.db)
                state = await engine.process_interaction(self.user_id, companion_id, current_user_message)
                anchors = await engine.anchor_service.get_anchors(self.user_id, companion_id, limit=3)
                compiled = RelationshipContextCompiler.compile(state, anchors)
                return [{"role": "system", "content": compiled}]

            # 2. Fallback to behavioral policy if relationship_service is provided
            if self.relationship_service and hasattr(self.relationship_service, "get_behavior_modifiers"):
                modifiers = await self.relationship_service.get_behavior_modifiers(companion_id)
                if modifiers:
                    lines = [
                        "[RELATIONSHIP CONTEXT — SOCIAL BOND]",
                        "Based on your established relationship with the user, apply the following conversational style:"
                    ]
                    for mod in modifiers:
                        lines.append(f"- {mod}")
                    lines.append("\n[RELATIONSHIP SAFETY BOUNDARIES]\n1. Never exhibit possessiveness or dependency.\n2. Respect the user's personal autonomy.")
                    return [{"role": "system", "content": "\n".join(lines)}]

            return []
        except Exception as e:
            logger.error(f"Failed to build relationship context: {e}")
            return []

