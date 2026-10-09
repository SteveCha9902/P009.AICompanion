from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, desc, asc
from app.db.models.memory import Memory, MemoryStatus
import logging

logger = logging.getLogger(__name__)

class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Memory:
        memory = Memory(**kwargs)
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def get_by_id(self, memory_id: str) -> Optional[Memory]:
        result = await self.session.execute(select(Memory).where(Memory.id == memory_id))
        return result.scalars().first()

    async def get_active_memories(self, companion_id: str, limit: int = 100) -> List[Memory]:
        result = await self.session.execute(
            select(Memory)
            .where(Memory.companion_id == companion_id)
            .where(Memory.status == MemoryStatus.ACTIVE)
            .order_by(desc(Memory.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_similar(
        self, 
        companion_id: str, 
        embedding: list, 
        limit: int = 5,
        threshold: float = 0.75
    ) -> List[tuple[Memory, float]]:
        # Using cosine distance (embedding.cosine_distance). 
        # Similarity = 1 - distance. So distance < 1 - threshold
        try:
            # We want to return both the memory and the similarity score
            # cosine_distance operator is '<=>' in pgvector
            distance_expr = Memory.embedding.cosine_distance(embedding)
            
            result = await self.session.execute(
                select(Memory, (1.0 - distance_expr).label("similarity"))
                .where(Memory.companion_id == companion_id)
                .where(Memory.status == MemoryStatus.ACTIVE)
                .where(distance_expr < (1.0 - threshold))
                .order_by(distance_expr)
                .limit(limit)
            )
            return [(row.Memory, row.similarity) for row in result.all()]
        except Exception as e:
            logger.debug(f"[MemoryRepository] Vector search fallback to active memories: {e}")
            # SQLite Fallback: return active memories with default similarity
            try:
                active_memories = await self.get_active_memories(companion_id, limit=limit)
                return [(m, 0.85) for m in active_memories]
            except Exception:
                return []

    async def update_status(self, memory_id: str, status: MemoryStatus) -> Optional[Memory]:
        memory = await self.get_by_id(memory_id)
        if memory:
            memory.status = status
            self.session.add(memory)
            await self.session.commit()
            await self.session.refresh(memory)
        return memory

    async def soft_delete(self, memory_id: str) -> bool:
        memory = await self.update_status(memory_id, MemoryStatus.DELETED)
        return memory is not None
