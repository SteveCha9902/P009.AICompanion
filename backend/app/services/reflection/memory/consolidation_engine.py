import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.memory import Memory, MemoryType, MemorySource, MemoryKind, MemoryStatus
from app.services.reflection.domain.reflection_result import MemoryCandidateDTO
from app.services.reflection.memory.duplicate_detector import DuplicateDetector

logger = logging.getLogger(__name__)

class MemoryConsolidationEngine:
    """
    Executes Memory Consolidation Actions: CREATE, MERGE, ARCHIVE, DISCARD.
    """

    @staticmethod
    async def consolidate(
        db: AsyncSession,
        companion_id: str,
        candidates: List[MemoryCandidateDTO]
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        for cand in candidates:
            # 1. Check for Discard (Low importance)
            if cand.importance < 0.50:
                actions.append({"action": "DISCARD", "content": cand.content, "reason": "Low importance score"})
                continue

            # 2. Check Duplicate Detector
            is_dup = await DuplicateDetector.is_duplicate(db, companion_id, cand.content)
            if is_dup:
                actions.append({"action": "MERGE", "content": cand.content, "reason": "Merged into existing memory record"})
                continue

            # 3. Create New Long-Term Memory Record
            mem_type = MemoryType.CHARACTER_INTERPRETATION
            if hasattr(MemoryType, cand.memory_type):
                mem_type = getattr(MemoryType, cand.memory_type)

            new_mem = Memory(
                id=str(uuid.uuid4()),
                companion_id=companion_id,
                type=mem_type,
                source=MemorySource.SYSTEM_DERIVED,
                kind=MemoryKind.PERSISTENT,
                status=MemoryStatus.ACTIVE,
                content=cand.content,
                importance=int(cand.importance * 100),
                confidence=0.9
            )
            db.add(new_mem)
            actions.append({"action": "CREATE", "content": cand.content, "memory_id": new_mem.id})

        await db.commit()
        return actions
