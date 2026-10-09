import logging
from app.db.models.notification import NotificationEvent, NotificationStatus
from app.repositories.notification_repository import NotificationRepository
from app.services.notifications.provider import BaseNotificationProvider
from app.services.notifications.policy import NotificationPolicyEngine
from app.db.models.presence import PresenceState
from app.db.models.message import Message

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(
        self, 
        repo: NotificationRepository, 
        provider: BaseNotificationProvider,
        policy_engine: NotificationPolicyEngine
    ):
        self.repo = repo
        self.provider = provider
        self.policy_engine = policy_engine

    async def deliver_message(
        self, 
        companion_id: str, 
        presence: PresenceState, 
        message: Message, 
        trigger_type: str = "PROACTIVE_MESSAGE",
        proactive_event_id: str = None
    ) -> NotificationEvent:
        settings = await self.repo.get_settings(companion_id)
        
        # 1. Create candidate event
        event = NotificationEvent(
            companion_id=companion_id,
            message_id=message.id,
            proactive_event_id=proactive_event_id,
            type=trigger_type,
            channel="PUSH"
        )
        event = await self.repo.create_event(event)

        # 2. Evaluate Policy
        should_push, reason = self.policy_engine.evaluate(presence, settings)
        
        if not should_push:
            logger.info(f"Notification {event.id} denied: {reason}")
            # Even if denied push, it might be delivered in-app when user opens
            await self.repo.update_status(event.id, NotificationStatus.DISMISSED)
            return event

        if not settings.push_token:
            logger.info(f"Notification {event.id} failed: No push token available.")
            await self.repo.update_status(event.id, NotificationStatus.FAILED)
            return event

        # 3. Prepare Payload
        body = message.content
        if not getattr(settings, 'notification_preview_enabled', True):
            body = "You have a new message."

        payload = {
            "title": "AI Companion",
            "body": body,
            "data": {
                "conversation_id": message.conversation_id,
                "deep_link": f"p009://conversation/{message.conversation_id}",
                "proactive_event_id": proactive_event_id
            }
        }

        # 4. Send via Provider
        await self.repo.update_status(event.id, NotificationStatus.QUEUED)
        success = await self.provider.send(settings.push_token, payload)

        if success:
            await self.repo.update_status(event.id, NotificationStatus.SENT)
        else:
            await self.repo.update_status(event.id, NotificationStatus.FAILED)

        return event
