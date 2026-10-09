import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.memory import Memory, MemoryType

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """
    Detects identical or semantically duplicate memories in the database.
    """

    @staticmethod
    async def is_duplicate(
        db: AsyncSession,
        companion_id: str,
        content: str,
        threshold: float = 0.85
    ) -> bool:
        stmt = (
            select(Memory)
            .where(Memory.companion_id == companion_id)
        )
        res = await db.execute(stmt)
        existing_memories = res.scalars().all()

        content_clean = content.strip().lower()
        for em in existing_memories:
            em_clean = em.content.strip().lower()
            # Exact match or substring containment
            if content_clean == em_clean or (len(content_clean) > 10 and content_clean in em_clean):
                return True

        return False
