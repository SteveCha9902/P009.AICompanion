from typing import Dict, Any, Optional
from app.services.notification.provider_interface import BaseNotificationProvider
import logging

logger = logging.getLogger(__name__)

class LocalNotificationProvider(BaseNotificationProvider):
    """
    Fallback provider for local development or when remote push is unavailable.
    Simulates sending a push notification.
    """
    async def send_notification(self, 
                                companion_id: str, 
                                device_token: str, 
                                title: str, 
                                body: str, 
                                data: Optional[Dict[str, Any]] = None) -> bool:
        logger.info(f"[LOCAL NOTIFICATION] To: {device_token} | Title: {title} | Body: {body} | Data: {data}")
        # In a real local scenario, this might trigger an in-app toast or just log
        return True
