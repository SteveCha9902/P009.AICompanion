from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from app.db.models.notification import NotificationEvent, NotificationStatus
from app.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

class BaseNotificationProvider(ABC):
    @abstractmethod
    async def send(self, token: str, payload: Dict[str, Any]) -> bool:
        """
        Send a notification to the specified token.
        Returns True if sent successfully, False otherwise.
        """
        pass

class ExpoNotificationProvider(BaseNotificationProvider):
    async def send(self, token: str, payload: Dict[str, Any]) -> bool:
        # Stub for Expo push notification sending.
        # In a real implementation, this would use the expo-server-sdk or raw HTTP API.
        logger.info(f"[EXPO PUSH STUB] Sending to {token} -> {payload}")
        return True

class MockNotificationProvider(BaseNotificationProvider):
    async def send(self, token: str, payload: Dict[str, Any]) -> bool:
        logger.info(f"[MOCK PUSH] Sending to {token} -> {payload}")
        return True
