from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models.reflection import ReflectionRecordModel
from app.services.reflection.reflection_service import ReflectionService

router = APIRouter(prefix="/reflections", tags=["Autonomous Thought & Reflection Engine"])

class ManualReflectionRequest(BaseModel):
    conversation_id: str = "default"
    companion_id: str = "default_companion"
    recent_messages: List[str] = ["오늘 프로젝트 첫 완성 버전을 배포했어!"]
    emotion_intensity: float = 0.85

@router.get("/history")
async def get_reflection_history(
    companion_id: str = Query(default="default_companion"),
    limit: int = Query(default=10),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns historical Reflection records.
    """
    try:
        stmt = (
            select(ReflectionRecordModel)
            .where(ReflectionRecordModel.companion_id == companion_id)
            .order_by(desc(ReflectionRecordModel.created_at))
            .limit(limit)
        )
        res = await db.execute(stmt)
        models = res.scalars().all()

        return [
            {
                "id": m.id,
                "companion_id": m.companion_id,
                "conversation_id": m.conversation_id,
                "trigger_type": m.trigger_type,
                "priority": m.priority,
                "importance_score": m.importance_score,
                "reflection_summary": m.reflection_summary,
                "emotional_pattern": m.emotional_pattern,
                "relationship_insight": m.relationship_insight,
                "behavioral_hints": m.behavioral_hints,
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            }
            for m in models
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{reflection_id}")
async def get_reflection_detail(
    reflection_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns single Reflection record detail.
    """
    stmt = select(ReflectionRecordModel).where(ReflectionRecordModel.id == reflection_id)
    res = await db.execute(stmt)
    model = res.scalars().first()
    if not model:
        raise HTTPException(status_code=404, detail="Reflection record not found")

    return {
        "id": model.id,
        "companion_id": model.companion_id,
        "conversation_id": model.conversation_id,
        "trigger_type": model.trigger_type,
        "priority": model.priority,
        "importance_score": model.importance_score,
        "reflection_summary": model.reflection_summary,
        "emotional_pattern": model.emotional_pattern,
        "relationship_insight": model.relationship_insight,
        "behavioral_hints": model.behavioral_hints,
        "status": model.status,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "completed_at": model.completed_at.isoformat() if model.completed_at else None,
    }

@router.post("/manual")
async def trigger_manual_reflection(
    req: ManualReflectionRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manual API for developer/testing trigger of autonomous reflection.
    """
    try:
        service = ReflectionService(db)
        record = await service.evaluate_and_reflect(
            companion_id=req.companion_id,
            conversation_id=req.conversation_id,
            recent_messages=req.recent_messages,
            emotion_intensity=req.emotion_intensity,
            is_manual=True
        )
        if not record:
            return {"status": "skipped_or_failed", "message": "Reflection did not complete or was rejected."}

        return {
            "status": "success",
            "reflection_id": record.id,
            "summary": record.reflection_summary,
            "hints": record.behavioral_hints
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
