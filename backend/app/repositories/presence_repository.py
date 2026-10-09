from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.presence import PresenceState, PresenceStateEnum
import logging

logger = logging.getLogger(__name__)

class PresenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, companion_id: str) -> Optional[PresenceState]:
        result = await self.session.execute(select(PresenceState).where(PresenceState.companion_id == companion_id))
        return result.scalars().first()

    async def save_state(self, state: PresenceState) -> PresenceState:
        existing = await self.get_state(state.companion_id)
        if existing:
            existing.state = state.state
            existing.last_active_at = state.last_active_at
            existing.last_interaction_at = state.last_interaction_at
            self.session.add(existing)
        else:
            self.session.add(state)
            existing = state
            
        await self.session.commit()
        await self.session.refresh(existing)
        return existing
