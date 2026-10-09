import asyncio
from typing import Dict, Any
from app.services.vision.provider_interface import BaseVisionProvider

class MockVisionProvider(BaseVisionProvider):
    async def analyze_frame(self, image_data: bytes) -> Dict[str, Any]:
        """Simulate vision analysis with a mock response."""
        await asyncio.sleep(0.5)  # Simulate latency
        
        # Mock logic based on image size to vary the response
        if len(image_data) % 2 == 0:
            return {
                "user_visible": True,
                "face_detected": True,
                "confidence": 0.95,
                "gaze": "toward_camera",
                "expression": "smiling",
                "objects": []
            }
        else:
            return {
                "user_visible": False,
                "face_detected": False,
                "confidence": 0.90,
                "gaze": "none",
                "expression": "none",
                "objects": ["coffee_cup"]
            }
