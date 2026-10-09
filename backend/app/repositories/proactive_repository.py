from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models.proactive import ProactiveEvent, ProactiveSettings
import logging

logger = logging.getLogger(__name__)

class ProactiveRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self, companion_id: str) -> ProactiveSettings:
        result = await self.session.execute(select(ProactiveSettings).where(ProactiveSettings.companion_id == companion_id))
        settings = result.scalars().first()
        
        if not settings:
            settings = ProactiveSettings(companion_id=companion_id)
            self.session.add(settings)
            await self.session.commit()
            await self.session.refresh(settings)
            
        return settings

    async def save_settings(self, settings: ProactiveSettings) -> ProactiveSettings:
        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(settings)
        return settings

    async def get_recent_events(self, companion_id: str, limit: int = 10) -> List[ProactiveEvent]:
        result = await self.session.execute(
            select(ProactiveEvent)
            .where(ProactiveEvent.companion_id == companion_id)
            .order_by(desc(ProactiveEvent.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def log_event(self, event: ProactiveEvent) -> ProactiveEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def update_event(self, event: ProactiveEvent) -> ProactiveEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
