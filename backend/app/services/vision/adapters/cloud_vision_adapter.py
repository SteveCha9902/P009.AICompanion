import os
import base64
import json
import logging
from typing import Dict, Any, Optional

from app.services.vision.provider_interface import BaseVisionProvider
from app.services.llm.base import (
    LLMProviderError,
    LLMAuthError,
    LLMTimeoutError
)

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

logger = logging.getLogger(__name__)

class CloudVisionProvider(BaseVisionProvider):
    """
    Production Cloud Vision Adapter using OpenAI gpt-4o-mini Vision.
    Extracts face, gaze, expression, objects, and confidence without storing raw images.
    """
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 20.0):
        if AsyncOpenAI is None:
            raise LLMProviderError("OpenAI SDK is not installed.", code="PROVIDER_CONFIG_ERROR")

        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            logger.warning("[CloudVisionProvider] OPENAI_API_KEY is missing.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

    def _ensure_client(self):
        if not self.client:
            raise LLMAuthError("OPENAI_API_KEY is missing for Cloud Vision Provider.")

    async def analyze_frame(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze a frame using OpenAI multimodal vision."""
        self._ensure_client()

        if not image_data or len(image_data) == 0:
            logger.warning("[CloudVisionProvider] Empty image data received.")
            return {
                "user_visible": False,
                "face_detected": False,
                "confidence": 0.0,
                "gaze": "none",
                "expression": "none",
                "objects": []
            }

        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            prompt = (
                "Analyze this front camera image for an AI companion in detail. Return a JSON object with:\n"
                "- 'user_visible' (boolean)\n"
                "- 'face_detected' (boolean)\n"
                "- 'confidence' (float 0.0 to 1.0)\n"
                "- 'gaze' ('toward_camera' | 'away' | 'screen' | 'none')\n"
                "- 'expression' ('smiling' | 'neutral' | 'curious' | 'focused' | 'tired' | 'none')\n"
                "- 'user_appearance' (clear Korean description of user's look: e.g., '안경을 쓴 남성, 단정한 헤어스타일')\n"
                "- 'clothing' (detailed Korean description of user's clothes: e.g., '회색/베이지색 지퍼 자켓 또는 셔츠')\n"
                "- 'scene_description' (detailed Korean description of the room, lighting, and background surroundings)\n"
                "- 'objects' (list of detected objects: e.g., ['glasses', 'jacket', 'office_interior', 'light'])."
            )

            response = await self.client.chat.completions.create(
                model=os.getenv("VISION_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=400
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)
            
            # Ensure safe fallbacks for schema
            return {
                "user_visible": bool(result.get("user_visible", False)),
                "face_detected": bool(result.get("face_detected", False)),
                "confidence": float(result.get("confidence", 0.8)),
                "gaze": str(result.get("gaze", "none")),
                "expression": str(result.get("expression", "none")),
                "user_appearance": str(result.get("user_appearance", "")),
                "clothing": str(result.get("clothing", "")),
                "scene_description": str(result.get("scene_description", "")),
                "objects": list(result.get("objects", []))
            }

        except openai.AuthenticationError as e:
            logger.error(f"[CloudVisionProvider] Auth failed: {e}")
            raise LLMAuthError(f"Vision Authentication failed: {e}", original_error=e)
        except (openai.APITimeoutError, TimeoutError) as e:
            logger.error(f"[CloudVisionProvider] Timeout: {e}")
            raise LLMTimeoutError(f"Vision Request Timed out: {e}", original_error=e)
        except Exception as e:
            logger.error(f"[CloudVisionProvider] Frame analysis failed: {e}")
            raise LLMProviderError(f"Vision Error: {e}", code="PROVIDER_VISION_ERROR", original_error=e)
