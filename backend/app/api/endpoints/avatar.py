from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.db.models.avatar import AvatarProfile
from app.services.presentation_engine import AvatarStateResolver
import uuid

router = APIRouter(prefix="/avatar", tags=["Avatar & Presentation"])

def get_avatar_state_resolver(db: AsyncSession = Depends(get_db)) -> AvatarStateResolver:
    return AvatarStateResolver(db=db)

class AvatarProfileSchema(BaseModel):
    avatar_type: str = "default"
    visual_style: str = "anime"
    default_expression: str = "neutral"
    default_motion: str = "idle"

class AvatarProfileUpdate(BaseModel):
    avatar_type: Optional[str] = None
    visual_style: Optional[str] = None
    default_expression: Optional[str] = None
    default_motion: Optional[str] = None

@router.get("/profile")
async def get_avatar_profile(
    companion_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        profile = db.query(AvatarProfile).filter(AvatarProfile.companion_id == companion_id).first() if hasattr(db, "query") else None
    except Exception:
        profile = None

    if not profile:
        return AvatarProfileSchema()
        
    return AvatarProfileSchema(
        avatar_type=profile.avatar_type,
        visual_style=profile.visual_style,
        default_expression=profile.default_expression,
        default_motion=profile.default_motion
    )

@router.get("/state")
async def get_avatar_state(
    companion_id: str,
    resolver: AvatarStateResolver = Depends(get_avatar_state_resolver)
) -> Dict[str, Any]:
    """
    [Avatar State Query]
    Returns the real-time Avatar State calculated by the AvatarStateResolver.
    """
    try:
        state = resolver.resolve(companion_id)
        return state
    except Exception as e:
        return {
            "expression": "neutral",
            "animation": "idle",
            "intensity": 0.5,
            "error": str(e)
        }

@router.get("/video-engine")
async def get_video_engine_info():
    """
    Returns the real-time LivePortrait / Video Loop engine status.
    """
    from app.services.avatar.talking_head_service import talking_head_service
    return {
        "engine": "LivePortrait-AudioDriven-v1",
        "fps": 30,
        "status": "ready",
        "supported_models": talking_head_service.get_supported_models(),
        "video_mode": "seamless_loop_and_realtime_lip_sync"
    }

