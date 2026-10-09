from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.notification import NotificationEvent, NotificationSettings, NotificationStatus
from datetime import datetime, timezone

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self, companion_id: str) -> NotificationSettings:
        result = await self.session.execute(select(NotificationSettings).where(NotificationSettings.companion_id == companion_id))
        settings = result.scalars().first()
        if not settings:
            settings = NotificationSettings(companion_id=companion_id)
            self.session.add(settings)
            await self.session.commit()
            await self.session.refresh(settings)
        return settings

    async def save_settings(self, settings: NotificationSettings) -> NotificationSettings:
        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(settings)
        return settings

    async def create_event(self, event: NotificationEvent) -> NotificationEvent:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
        
    async def get_event(self, event_id: str) -> Optional[NotificationEvent]:
        result = await self.session.execute(select(NotificationEvent).where(NotificationEvent.id == event_id))
        return result.scalars().first()

    async def update_status(self, event_id: str, status: NotificationStatus) -> Optional[NotificationEvent]:
        event = await self.get_event(event_id)
        if event:
            event.status = status
            now = datetime.now(timezone.utc)
            if status == NotificationStatus.SENT:
                event.sent_at = now
            elif status == NotificationStatus.DELIVERED:
                event.delivered_at = now
            elif status == NotificationStatus.OPENED:
                event.opened_at = now
                
            self.session.add(event)
            await self.session.commit()
            await self.session.refresh(event)
        return event
