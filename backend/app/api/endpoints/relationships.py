from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Dict
import logging

from app.db.session import get_db
from app.services.relationship.relationship_engine import RelationshipEngine
from app.services.relationship.relationship_anchor_service import RelationshipAnchorService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/relationships/current")
async def get_current_relationship(
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns the comprehensive 7-Dimensional Social Bond Profile.
    """
    try:
        engine = RelationshipEngine(db)
        state = await engine.get_or_create_state(user_id=x_user_id, companion_id=companion_id)
        
        return {
            "user_id": state.user_id,
            "companion_id": state.companion_id,
            "stage": state.stage.value,
            "stage_display": state.stage.value.replace("_", " ").upper(),
            "dimensions": state.dimensions.model_dump(),
            "recent_presence": state.recent_presence,
            "total_conversations": state.total_conversations,
            "last_interacted_at": state.last_interacted_at.isoformat() if state.last_interacted_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/anchors")
async def get_relationship_anchors(
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    limit: int = Query(default=10),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns immutable relational anchors (first meeting, confession, milestone stages).
    """
    try:
        anchor_service = RelationshipAnchorService(db)
        anchors = await anchor_service.get_anchors(user_id=x_user_id, companion_id=companion_id, limit=limit)
        return [a.model_dump() for a in anchors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/timeline")
async def get_relationship_timeline(
    x_user_id: str = Header(default="default_user"),
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns the complete relationship story timeline.
    """
    try:
        engine = RelationshipEngine(db)
        state = await engine.get_or_create_state(user_id=x_user_id, companion_id=companion_id)
        anchors = await engine.anchor_service.get_anchors(user_id=x_user_id, companion_id=companion_id, limit=20)
        
        return {
            "current_stage": state.stage.value,
            "total_conversations": state.total_conversations,
            "milestones": [a.model_dump() for a in anchors]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

