import asyncio
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.memory import MemoryStatus
from app.repositories.memory_repository import MemoryRepository
from app.repositories.companion_repository import CompanionRepository
from app.repositories.message_repository import MessageRepository
from app.services.memory.extractor import MemoryExtractor
from app.services.memory.validator import MemoryValidator
from app.services.memory.embedding import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(
        self,
        session: AsyncSession,
        memory_repo: MemoryRepository,
        companion_repo: CompanionRepository,
        msg_repo: MessageRepository,
        embedding_provider: BaseEmbeddingProvider,
        extractor: MemoryExtractor,
        validator: MemoryValidator
    ):
        self.session = session
        self.memory_repo = memory_repo
        self.companion_repo = companion_repo
        self.msg_repo = msg_repo
        self.embedding_provider = embedding_provider
        self.extractor = extractor
        self.validator = validator

    async def process_conversation_for_memory(self, user_id: str, conversation_id: str):
        """
        Background task to extract and validate memories after a conversation exchange.
        """
        try:
            companion = await self.companion_repo.get_by_user_id(user_id)
            if not companion:
                return

            # 1. Fetch recent messages
            messages = await self.msg_repo.get_by_conversation_id(conversation_id, limit=5)
            # Reorder chronologically
            messages.reverse()
            
            history = [{"role": m.role, "content": m.content} for m in messages]

            # 2. Extract Memory Candidates
            candidates = await self.extractor.extract(history)
            if not candidates:
                return

            # 3. Process each candidate
            for candidate in candidates:
                await self._process_candidate(companion.id, candidate, conversation_id)
                
        except Exception as e:
            logger.error(f"Failed to process memory: {e}")

    async def _process_candidate(self, companion_id: str, candidate: Dict[str, Any], conversation_id: str):
        try:
            # Create a string representation to embed for validation search
            content_str = f"{candidate.get('subject')} {candidate.get('content')}"
            candidate_embedding = await self.embedding_provider.embed(content_str)

            # Search similar to check for duplicates/conflicts
            similar_memories = await self.memory_repo.search_similar(
                companion_id=companion_id,
                embedding=candidate_embedding,
                limit=5,
                threshold=0.60
            )
            
            existing_mems = [m for m, score in similar_memories]

            # Determine relationship
            relation, target_id = await self.validator.determine_relation(candidate, existing_mems)

            if relation == MemoryRelation.DUPLICATE and target_id:
                # Update confidence and timestamp
                mem = await self.memory_repo.get_by_id(target_id)
                if mem:
                    # simplistic update
                    mem.confidence = min(1.0, mem.confidence + 0.1)
                    self.session.add(mem)
                    await self.session.commit()
            
            elif relation in (MemoryRelation.CONTRADICTORY, MemoryRelation.TEMPORAL_UPDATE) and target_id:
                # Supersede old, create new
                await self.memory_repo.update_status(target_id, MemoryStatus.SUPERSEDED)
                await self._create_memory_from_candidate(companion_id, candidate, candidate_embedding, conversation_id)
            
            elif relation in (MemoryRelation.COMPLEMENTARY, MemoryRelation.NEW):
                # Just create new
                await self._create_memory_from_candidate(companion_id, candidate, candidate_embedding, conversation_id)

        except Exception as e:
            logger.error(f"Failed to process candidate {candidate}: {e}")
            # Try to store it anyway without vector search if embedding failed
            try:
                if 'embedding' in locals():
                    del candidate_embedding
                await self._create_memory_from_candidate(companion_id, candidate, None, conversation_id)
            except Exception as inner_e:
                logger.error(f"Fallback save failed: {inner_e}")

    async def _create_memory_from_candidate(self, companion_id: str, candidate: Dict[str, Any], embedding: list, conversation_id: str):
        await self.memory_repo.create(
            companion_id=companion_id,
            type=candidate.get("type", "PERSONAL_FACT"),
            source=candidate.get("source", "INFERRED"),
            kind=candidate.get("kind", "PERSISTENT"),
            content=candidate.get("content", ""),
            subject=candidate.get("subject"),
            entity=candidate.get("entity"),
            polarity=candidate.get("polarity"),
            importance=candidate.get("importance", 50),
            confidence=candidate.get("confidence", 0.8),
            source_conversation_id=conversation_id,
            embedding=embedding
        )
