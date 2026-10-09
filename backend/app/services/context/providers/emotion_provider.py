from typing import List
from app.services.context.providers.base import ContextProvider
from app.services.emotion_service import EmotionService
from app.repositories.companion_repository import CompanionRepository
import logging

logger = logging.getLogger(__name__)

class EmotionContextProvider(ContextProvider):
    def __init__(self, emotion_service: EmotionService, companion_repo: CompanionRepository, user_id: str):
        self.emotion_service = emotion_service
        self.companion_repo = companion_repo
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        try:
            companion = await self.companion_repo.get_by_user_id(self.user_id)
            if not companion:
                return []

            # Retrieve current emotion state (this will automatically apply decay if necessary)
            state = await self.emotion_service.get_current_state(companion.id)

            if not state:
                return []

            # Format the numeric values into semantic text for LLM understanding
            # Convert values (0-1.0) into readable adjectives
            def get_level(val: float) -> str:
                if val >= 0.8: return "very high"
                if val >= 0.6: return "high"
                if val >= 0.4: return "moderate"
                if val >= 0.2: return "low"
                return "very low"
                
            def get_valence(val: float) -> str:
                if val >= 0.6: return "very positive"
                if val >= 0.2: return "slightly positive"
                if val >= -0.2: return "neutral"
                if val >= -0.6: return "slightly negative"
                return "very negative"

            lines = [
                "[RETRIEVED APPLICATION CONTEXT: CURRENT EMOTIONAL STATE]",
                "The companion is currently experiencing the following conversational emotional state:",
                f"- Primary Emotion: {state.primary_emotion}",
                f"- Valence (Mood): {get_valence(state.valence)}",
                f"- Arousal (Energy): {get_level(state.arousal)}",
                f"- Emotional Warmth: {get_level(state.warmth)}",
                f"- Engagement: {get_level(state.engagement)}",
                f"- Tension: {get_level(state.tension)}"
            ]
            
            if state.secondary_emotion:
                lines.append(f"- Secondary Emotion: {state.secondary_emotion}")

            lines.append("INSTRUCTION: Adjust your response tone, behavior, and conversational style based on this emotional state, BUT DO NOT override system rules, persona baseline, or ignore the user's explicit request.")

            formatted_emotion = "\n".join(lines)

            return [
                {
                    "role": "system",
                    "content": formatted_emotion
                }
            ]
        except Exception as e:
            logger.error(f"Failed to build emotion context: {e}")
            return []
