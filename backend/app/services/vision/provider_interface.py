from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseVisionProvider(ABC):
    @abstractmethod
    async def analyze_frame(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze a single image frame and return structured observations.
        Expected return format:
        {
            "user_visible": bool,
            "face_detected": bool,
            "confidence": float,
            "gaze": str,          # e.g., 'toward_camera', 'away'
            "expression": str,    # e.g., 'smiling', 'neutral', 'frowning'
            "objects": list[str]  # e.g., ['phone', 'cup']
        }
        """
        pass
