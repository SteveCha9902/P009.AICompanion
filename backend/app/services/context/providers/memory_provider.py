from typing import List, Optional
from app.services.context.providers.base import ContextProvider
from app.services.memory.retriever import MemoryRetriever
from app.repositories.companion_repository import CompanionRepository
from app.services.shared_experience.shared_experience_engine import SharedExperienceEngine
from app.services.memory.autobiographical_context_compiler import AutobiographicalContextCompiler
import logging

logger = logging.getLogger(__name__)

class MemoryContextProvider(ContextProvider):
    def __init__(
        self,
        memory_retriever: MemoryRetriever,
        companion_repo: CompanionRepository,
        user_id: str,
        db=None,
        companion_id: Optional[str] = None
    ):
        self.memory_retriever = memory_retriever
        self.companion_repo = companion_repo
        self.user_id = user_id
        self.db = db
        self.companion_id = companion_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        try:
            companion_id = self.companion_id or "default_companion"
            if not self.companion_id and self.companion_repo:
                try:
                    companion = await self.companion_repo.get_by_user_id(self.user_id)
                    if companion:
                        companion_id = companion.id
                except Exception:
                    pass

            context_parts: List[str] = []

            # 1. Semantic Memory Retrieval (Facts / Preferences)
            if self.memory_retriever:
                try:
                    memories = await self.memory_retriever.retrieve(
                        companion_id=companion_id,
                        query=current_user_message,
                        top_k=5,
                        user_id=self.user_id
                    )
                    # 1.1 Secondary Defense: Validate Context Injection Scope
                    if hasattr(self.memory_retriever, "guard") and self.memory_retriever.guard:
                        memories = self.memory_retriever.guard.validate_context_injection(
                            user_id=self.user_id,
                            companion_id=companion_id,
                            memories=memories
                        )

                    if memories:
                        lines = ["[RETRIEVED APPLICATION CONTEXT: MEMORY]", "KNOWN USER INFORMATION:"]
                        for m in memories:
                            conf = m.confidence if getattr(m, 'confidence', None) is not None else 1.0
                            lines.append(f"- {m.content} (Confidence: {conf:.2f}, Type: {m.type})")
                        context_parts.append("\n".join(lines))
                except Exception as mem_err:
                    logger.warn(f"[MemoryContextProvider] Semantic retrieval error: {mem_err}")

            # 2. Autobiographical Memory & Shared Experience (DB integration)
            if self.db:
                try:
                    shared_engine = SharedExperienceEngine(self.db)
                    chapters = await shared_engine.get_story_chapters(self.user_id, companion_id)
                    auto_compiled = AutobiographicalContextCompiler.compile(
                        chapters=chapters,
                        shared_experiences=[],
                        recent_life_events=[]
                    )
                    context_parts.append(auto_compiled)
                except Exception as auto_err:
                    logger.warn(f"[MemoryContextProvider] Autobiographical compilation error: {auto_err}")

            if not context_parts:
                return []

            return [{"role": "system", "content": "\n\n".join(context_parts)}]
        except Exception as e:
            logger.error(f"Failed to build memory context: {e}")
            return []

