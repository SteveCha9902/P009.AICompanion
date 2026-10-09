from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy import select, delete

from app.db.session import get_db
from app.services.shared_experience.shared_experience_engine import SharedExperienceEngine
from app.services.memory.autobiographical_narrative_service import AutobiographicalNarrativeService
from app.db.models.autobiographical_memory import (
    LifeEventModel,
    SharedExperienceModel,
    EpisodicMemoryModel,
    TimelineEventModel,
    StoryChapterModel
)

router = APIRouter(prefix="/memory", tags=["Autobiographical Memory & Shared Life Timeline"])

class NarrativeRequest(BaseModel):
    topic: Optional[str] = "our_history"

class SelectiveForgetRequest(BaseModel):
    keyword: str

@router.get("/timeline")
async def get_timeline(
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    limit: int = Query(default=20),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns the chronologically ordered Shared Life Timeline events.
    """
    try:
        engine = SharedExperienceEngine(db)
        events = await engine.get_timeline(user_id=x_user_id, companion_id=companion_id, limit=limit)
        return [e.model_dump() for e in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/story")
async def get_story_chapters(
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns overarching Story Chapters grouping key relational and project milestones.
    """
    try:
        engine = SharedExperienceEngine(db)
        chapters = await engine.get_story_chapters(user_id=x_user_id, companion_id=companion_id)
        return [c.model_dump() for c in chapters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/life-events")
async def get_life_events(
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    limit: int = Query(default=20),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns high-importance promoted Life Events.
    """
    try:
        stmt = (
            select(LifeEventModel)
            .where(
                LifeEventModel.user_id == x_user_id,
                LifeEventModel.companion_id == companion_id
            )
            .limit(limit)
        )
        res = await db.execute(stmt)
        models = res.scalars().all()
        return [
            {
                "id": m.id,
                "title": m.title,
                "summary": m.summary,
                "category": m.category,
                "occurred_at": m.occurred_at.isoformat() if m.occurred_at else None,
                "importance": m.importance
            }
            for m in models
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/narrative")
async def generate_narrative(
    req: NarrativeRequest,
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generates a cohesive retrospective narrative of the shared journey.
    """
    try:
        engine = SharedExperienceEngine(db)
        chapters = await engine.get_story_chapters(user_id=x_user_id, companion_id=companion_id)
        timeline = await engine.get_timeline(user_id=x_user_id, companion_id=companion_id, limit=10)
        
        narrative_text = AutobiographicalNarrativeService.generate_narrative(chapters, timeline, req.topic)
        return {
            "narrative": narrative_text,
            "chapters_included": len(chapters),
            "timeline_events_included": len(timeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/selective-forget")
async def selective_forget(
    req: SelectiveForgetRequest,
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Selectively forgets memories matching keyword across Episodic, Life Event, and Timeline tables.
    """
    try:
        kw = f"%{req.keyword}%"
        # 1. Delete matching Life Events
        await db.execute(
            delete(LifeEventModel)
            .where(
                LifeEventModel.user_id == x_user_id,
                LifeEventModel.summary.like(kw)
            )
        )
        # 2. Delete matching Timeline Events
        await db.execute(
            delete(TimelineEventModel)
            .where(
                TimelineEventModel.user_id == x_user_id,
                TimelineEventModel.summary.like(kw)
            )
        )
        # 3. Delete matching Episodic Memories
        await db.execute(
            delete(EpisodicMemoryModel)
            .where(
                EpisodicMemoryModel.user_id == x_user_id,
                EpisodicMemoryModel.summary.like(kw)
            )
        )
        await db.commit()

        return {"status": "success", "keyword_forgotten": req.keyword}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
