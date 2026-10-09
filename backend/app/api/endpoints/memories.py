from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
import logging

from app.db.session import get_db
from app.repositories.memory_repository import MemoryRepository
from app.repositories.companion_repository import CompanionRepository

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/memories")
async def get_memories(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    memory_repo = MemoryRepository(db)
    
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        return []
        
    memories = await memory_repo.get_active_memories(companion.id)
    
    # Return formatted memories
    return [
        {
            "id": m.id,
            "type": m.type,
            "source": m.source,
            "content": m.content,
            "subject": m.subject,
            "entity": m.entity,
            "importance": m.importance,
            "confidence": m.confidence,
            "created_at": m.created_at,
            "source_conversation_id": m.source_conversation_id
        } for m in memories
    ]

@router.get("/memories/{memory_id}")
async def get_memory(
    memory_id: str,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    memory_repo = MemoryRepository(db)
    companion_repo = CompanionRepository(db)
    
    memory = await memory_repo.get_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
        
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion or memory.companion_id != companion.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return {
        "id": memory.id,
        "type": memory.type,
        "source": memory.source,
        "content": memory.content,
        "subject": memory.subject,
        "entity": memory.entity,
        "importance": memory.importance,
        "confidence": memory.confidence,
        "created_at": memory.created_at,
        "source_conversation_id": memory.source_conversation_id
    }

@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: str,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    memory_repo = MemoryRepository(db)
    companion_repo = CompanionRepository(db)
    
    memory = await memory_repo.get_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
        
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion or memory.companion_id != companion.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    success = await memory_repo.soft_delete(memory_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete memory")
        
    return {"status": "success", "id": memory_id}
