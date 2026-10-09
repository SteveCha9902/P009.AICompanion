from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models.relationship import RelationshipState, RelationshipEvent
import logging

logger = logging.getLogger(__name__)

class RelationshipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, companion_id: str) -> Optional[RelationshipState]:
        result = await self.session.execute(select(RelationshipState).where(RelationshipState.companion_id == companion_id))
        return result.scalars().first()

    async def save_state(self, state: RelationshipState) -> RelationshipState:
        existing = await self.get_state(state.companion_id)
        if existing:
            existing.trust = state.trust
            existing.familiarity = state.familiarity
            existing.closeness = state.closeness
            existing.engagement = state.engagement
            existing.reliability = state.reliability
            existing.relationship_level = state.relationship_level
            self.session.add(existing)
        else:
            self.session.add(state)
            existing = state
            
        await self.session.commit()
        await self.session.refresh(existing)
        return existing

    async def log_event(self, event: RelationshipEvent) -> RelationshipEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_recent_events(self, companion_id: str, limit: int = 20) -> List[RelationshipEvent]:
        result = await self.session.execute(
            select(RelationshipEvent)
            .where(RelationshipEvent.companion_id == companion_id)
            .order_by(desc(RelationshipEvent.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
