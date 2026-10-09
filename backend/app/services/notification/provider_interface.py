from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseNotificationProvider(ABC):
    @abstractmethod
    async def send_notification(self, 
                                companion_id: str, 
                                device_token: str, 
                                title: str, 
                                body: str, 
                                data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sends a notification to the user's device.
        Returns True if successful, False otherwise.
        """
        pass
