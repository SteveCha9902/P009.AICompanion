import os
import json
import openai
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EmotionExtractor:
    def __init__(self, model: str = "gpt-4o", api_key: str = None):
        self.model = model
        key = api_key or os.getenv("OPENAI_API_KEY") or "mock_key_for_dev_mode"
        self.client = openai.AsyncOpenAI(api_key=key)

    async def extract_signal(self, current_message: str, conversation_history: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """
        Analyze the current user message and recent history to extract an Emotion Signal.
        This does NOT decide the Companion's final emotion, it only extracts the user's emotion and the trigger.
        """
        history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history[-5:]])

        system_prompt = """
You are the Emotion Extractor for an AI Companion.
Your task is to analyze the user's latest message (along with recent history) and extract an "Emotion Signal".

Do NOT determine the companion's response emotion.
ONLY determine the user's emotion, the trigger event (if any), and the emotional intensity.

Output a JSON object with the following schema:
{
  "user_emotion": "<JOY|SADNESS|ANGER|FEAR|SURPRISE|CALM|CURIOSITY|AFFECTION|FRUSTRATION|NEUTRAL>",
  "trigger": "<Short description of the event or topic causing the emotion, or null>",
  "intensity": <Float between 0.0 (very weak) and 1.0 (very strong)>,
  "confidence": <Float between 0.0 and 1.0>
}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"History:\n{history_text}\n\nCurrent Message: {current_message}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return parsed
        except Exception as e:
            logger.error(f"Failed to extract emotion signal: {e}")
            return None
