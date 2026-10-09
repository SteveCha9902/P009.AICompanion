from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc

from app.db.models.autobiographical_memory import TimelineEventModel, LifeEventModel, StoryChapterModel
from app.domain.memory.timeline_event import TimelineEvent
from app.domain.memory.life_event import LifeEvent, LifeEventCategory

class TemporalMemoryRetriever:
    """
    Retrieves events based on temporal keywords ('first time', 'when did we', 'recently')
    and chronological sequence.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_query(
        self,
        query: str,
        user_id: str = "default_user",
        companion_id: str = "default_companion"
    ) -> List[TimelineEvent]:
        q_lower = query.lower()

        is_first_inquiry = any(kw in q_lower for kw in ["처음", "언제", "시작", "first time", "when did we"])
        order_clause = asc(TimelineEventModel.occurred_at) if is_first_inquiry else desc(TimelineEventModel.occurred_at)

        stmt = (
            select(TimelineEventModel)
            .where(
                TimelineEventModel.user_id == user_id,
                TimelineEventModel.companion_id == companion_id
            )
            .order_by(order_clause)
            .limit(5)
        )
        res = await self.db.execute(stmt)
        models = res.scalars().all()

        return [
            TimelineEvent(
                id=m.id,
                user_id=m.user_id,
                companion_id=m.companion_id,
                occurred_at=m.occurred_at,
                title=m.title,
                summary=m.summary,
                importance=m.importance,
                event_type=m.event_type
            )
            for m in models
        ]
