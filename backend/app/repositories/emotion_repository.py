from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models.emotion import EmotionState, EmotionEvent
import logging

logger = logging.getLogger(__name__)

class EmotionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, companion_id: str) -> Optional[EmotionState]:
        result = await self.session.execute(select(EmotionState).where(EmotionState.companion_id == companion_id))
        return result.scalars().first()

    async def save_state(self, state: EmotionState) -> EmotionState:
        # Check if exists
        existing = await self.get_state(state.companion_id)
        if existing:
            existing.primary_emotion = state.primary_emotion
            existing.secondary_emotion = state.secondary_emotion
            existing.valence = state.valence
            existing.arousal = state.arousal
            existing.warmth = state.warmth
            existing.engagement = state.engagement
            existing.tension = state.tension
            existing.confidence = state.confidence if state.confidence is not None else (existing.confidence or 1.0)
            existing.last_trigger_at = state.last_trigger_at
            self.session.add(existing)
        else:
            if state.confidence is None:
                state.confidence = 1.0
            self.session.add(state)
            existing = state

            
        await self.session.commit()
        await self.session.refresh(existing)
        return existing

    async def log_event(self, event: EmotionEvent) -> EmotionEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_recent_events(self, companion_id: str, limit: int = 20) -> List[EmotionEvent]:
        result = await self.session.execute(
            select(EmotionEvent)
            .where(EmotionEvent.companion_id == companion_id)
            .order_by(desc(EmotionEvent.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
