from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
import logging

from app.db.session import get_db
from app.repositories.emotion_repository import EmotionRepository
from app.repositories.companion_repository import CompanionRepository
from app.repositories.persona_repository import PersonaRepository
from app.services.emotion_service import EmotionService
from app.services.emotion.extractor import EmotionExtractor
from app.services.emotion.transition import TransitionEngine
from app.services.emotion.decay import DecayEngine

logger = logging.getLogger(__name__)
router = APIRouter()

def get_emotion_service(db: AsyncSession) -> EmotionService:
    emotion_repo = EmotionRepository(db)
    companion_repo = CompanionRepository(db)
    persona_repo = PersonaRepository(db)
    extractor = EmotionExtractor()
    transition_engine = TransitionEngine()
    decay_engine = DecayEngine()
    return EmotionService(db, emotion_repo, companion_repo, persona_repo, extractor, transition_engine, decay_engine)

@router.get("/emotions/current")
async def get_current_emotion(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    emotion_service = get_emotion_service(db)
    state = await emotion_service.get_current_state(companion.id)

    return {
        "id": state.id,
        "primary_emotion": state.primary_emotion,
        "secondary_emotion": state.secondary_emotion,
        "valence": state.valence,
        "arousal": state.arousal,
        "warmth": state.warmth,
        "engagement": state.engagement,
        "tension": state.tension,
        "updated_at": state.updated_at
    }

@router.get("/emotions/history")
async def get_emotion_history(
    x_user_id: str = Header(...),
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    companion_repo = CompanionRepository(db)
    companion = await companion_repo.get_by_user_id(x_user_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")

    emotion_repo = EmotionRepository(db)
    events = await emotion_repo.get_recent_events(companion.id, limit=limit)

    return [
        {
            "id": ev.id,
            "event_type": ev.event_type,
            "trigger": ev.trigger,
            "previous_state": ev.previous_state,
            "new_state": ev.new_state,
            "intensity": ev.intensity,
            "created_at": ev.created_at
        } for ev in events
    ]
