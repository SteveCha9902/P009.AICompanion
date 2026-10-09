import os
import json
import openai
from typing import List, Dict, Any
import logging
from app.db.models.memory import MemoryType

logger = logging.getLogger(__name__)

class MemoryExtractor:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def extract(self, conversation_history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Analyze recent conversation history and extract memory candidates.
        Returns a list of dictionaries representing memory candidates.
        """
        
        system_prompt = f"""
You are the Memory Extraction Engine for an AI Companion.
Your task is to analyze the recent conversation and extract long-term useful facts, preferences, goals, habits, etc. about the user or the relationship.

Do NOT extract transient chat (e.g., "I'm having lunch now", "Hello").
Do NOT guess or fabricate.

For each memory, output a JSON object in a list with the following schema:
- type: one of {', '.join([t.value for t in MemoryType])}
- source: "USER_EXPLICIT" (User explicitly stated this fact) or "INFERRED" (You deduced it from their behavior/statements)
- kind: "PERSISTENT", "TEMPORARY", or "EPISODIC"
- content: Clear, concise summary of the fact (e.g., "User loves Fujifilm cameras.")
- subject: A short topic word (e.g., "camera", "food", "family")
- entity: The specific entity if applicable (e.g., "Fujifilm", "Pizza")
- polarity: "positive", "negative", or "neutral"
- importance: An integer from 0 to 100 representing how critical this is for long-term companion relationship.
- confidence: A float from 0.0 to 1.0 representing how certain you are of this fact.

Return ONLY a valid JSON array of these objects. If nothing to extract, return [].
"""

        # Format conversation for the prompt
        formatted_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history])

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract memories from the following conversation:\n\n{formatted_history}"}
                ],
                response_format={ "type": "json_object" }, # Assuming we wrap the array in an object to ensure validity
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            # The prompt asks for an array, but if we use json_object it might return {"memories": [...]}
            # Let's handle both.
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                candidates = parsed.get("memories", [])
            elif isinstance(parsed, list):
                candidates = parsed
            else:
                candidates = []
                
            return candidates

        except Exception as e:
            logger.error(f"Failed to extract memories: {e}")
            return []
