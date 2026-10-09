from fastapi import APIRouter, Depends, Header, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import logging

from app.db.session import get_db
from app.repositories.notification_repository import NotificationRepository
from app.repositories.companion_repository import CompanionRepository

logger = logging.getLogger(__name__)
router = APIRouter()

class PushTokenRegisterRequest(BaseModel):
    token: str

class NotificationSettingsUpdate(BaseModel):
    notifications_enabled: Optional[bool]
    proactive_messages_enabled: Optional[bool]
    notification_preview_enabled: Optional[bool]
    never_disturb: Optional[bool]

@router.post("/notifications/token")
async def register_push_token(
    request: PushTokenRegisterRequest,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    repo = NotificationRepository(db)
    settings = await repo.get_settings(companion.id)
    settings.push_token = request.token
    await repo.save_settings(settings)
    return {"status": "success"}

@router.get("/notifications/settings")
async def get_notification_settings(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    repo = NotificationRepository(db)
    settings = await repo.get_settings(companion.id)

    return {
        "notifications_enabled": settings.notifications_enabled,
        "proactive_messages_enabled": settings.proactive_messages_enabled,
        "notification_preview_enabled": settings.notification_preview_enabled,
        "never_disturb": settings.never_disturb
    }

@router.put("/notifications/settings")
async def update_notification_settings(
    update_data: NotificationSettingsUpdate,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    repo = NotificationRepository(db)
    settings = await repo.get_settings(companion.id)
    
    if update_data.notifications_enabled is not None:
        settings.notifications_enabled = update_data.notifications_enabled
    if update_data.proactive_messages_enabled is not None:
        settings.proactive_messages_enabled = update_data.proactive_messages_enabled
    if update_data.notification_preview_enabled is not None:
        settings.notification_preview_enabled = update_data.notification_preview_enabled
    if update_data.never_disturb is not None:
        settings.never_disturb = update_data.never_disturb

    await repo.save_settings(settings)
    return {"status": "success"}
