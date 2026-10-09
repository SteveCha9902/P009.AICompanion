from fastapi import APIRouter, Depends, Header, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
import logging

from app.db.session import get_db
from app.repositories.proactive_repository import ProactiveRepository
from app.repositories.companion_repository import CompanionRepository

logger = logging.getLogger(__name__)
router = APIRouter()

class ProactiveSettingsUpdate(BaseModel):
    enabled: Optional[bool]
    daily_limit: Optional[int]
    cooldown_minutes: Optional[int]
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]

@router.get("/proactive/settings")
async def get_proactive_settings(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    repo = ProactiveRepository(db)
    settings = await repo.get_settings(companion.id)

    return {
        "enabled": settings.enabled,
        "daily_limit": settings.daily_limit,
        "cooldown_minutes": settings.cooldown_minutes,
        "quiet_hours_start": settings.quiet_hours_start,
        "quiet_hours_end": settings.quiet_hours_end
    }

@router.put("/proactive/settings")
async def update_proactive_settings(
    update_data: ProactiveSettingsUpdate,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    repo = ProactiveRepository(db)
    settings = await repo.get_settings(companion.id)
    
    if update_data.enabled is not None:
        settings.enabled = update_data.enabled
    if update_data.daily_limit is not None:
        settings.daily_limit = update_data.daily_limit
    if update_data.cooldown_minutes is not None:
        settings.cooldown_minutes = update_data.cooldown_minutes
    if update_data.quiet_hours_start is not None:
        settings.quiet_hours_start = update_data.quiet_hours_start
    if update_data.quiet_hours_end is not None:
        settings.quiet_hours_end = update_data.quiet_hours_end

    await repo.save_settings(settings)
    return {"status": "success"}

@router.get("/proactive/history")
async def get_proactive_history(
    x_user_id: str = Header(...),
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    repo = ProactiveRepository(db)
    events = await repo.get_recent_events(companion.id, limit=limit)

    return [
        {
            "id": ev.id,
            "trigger_type": ev.trigger_type,
            "decision": ev.decision,
            "score": ev.score,
            "decision_reason": ev.decision_reason,
            "created_at": ev.created_at
        } for ev in events
    ]
