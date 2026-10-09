from fastapi import APIRouter, Depends, Header, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
import logging

from app.db.session import get_db
from app.repositories.presence_repository import PresenceRepository
from app.repositories.companion_repository import CompanionRepository
from app.services.presence_service import PresenceService

logger = logging.getLogger(__name__)
router = APIRouter()

class HeartbeatRequest(BaseModel):
    is_foreground: bool

@router.get("/presence")
async def get_presence(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    presence_repo = PresenceRepository(db)
    presence_service = PresenceService(presence_repo)
    state = await presence_service.get_state(companion.id)

    return {
        "state": state.state,
        "last_active_at": state.last_active_at,
        "last_interaction_at": state.last_interaction_at
    }

@router.post("/presence/heartbeat")
async def update_heartbeat(
    request: HeartbeatRequest,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    presence_repo = PresenceRepository(db)
    presence_service = PresenceService(presence_repo)
    
    state = await presence_service.update_heartbeat(companion.id, request.is_foreground)

    return {
        "status": "success",
        "state": state.state
    }
