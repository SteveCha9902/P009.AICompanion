from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.context.providers.base import ContextProvider
from app.services.reflection.reflection_service import ReflectionService
import logging

logger = logging.getLogger(__name__)

class ReflectionContextProvider(ContextProvider):
    """
    Injects high-level Recent Reflection Insights into ContextBuilder (<150 tokens).
    Does NOT alter Persona, only supplies recent emotional/relational context hints.
    """

    def __init__(self, db: Optional[AsyncSession] = None, companion_id: str = "default_companion"):
        self.db = db
        self.companion_id = companion_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, Any]]:
        if not self.db:
            return []

        try:
            service = ReflectionService(self.db)
            records = await service.get_recent_insights(self.companion_id, limit=1)
            if not records:
                return []

            rec = records[0]
            lines = [
                "[RECENT REFLECTION INSIGHT]",
                f"- Summary: {rec.reflection_summary}",
            ]
            if rec.behavioral_hints:
                lines.append(f"- Preferred Focus: {', '.join(rec.behavioral_hints[:3])}")

            return [{
                "role": "system",
                "content": "\n".join(lines)
            }]
        except Exception as e:
            logger.warning(f"[ReflectionContextProvider] Error building context: {e}")
            return []
