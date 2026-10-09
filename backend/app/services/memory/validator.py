import os
import json
import openai
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class MemoryRelation(str):
    DUPLICATE = "DUPLICATE"
    CONTRADICTORY = "CONTRADICTORY"
    COMPLEMENTARY = "COMPLEMENTARY"
    TEMPORAL_UPDATE = "TEMPORAL_UPDATE"
    NEW = "NEW"

class MemoryValidator:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def determine_relation(self, candidate: Dict[str, Any], existing_memories: List[Any]) -> Tuple[str, Any]:
        """
        Compare the candidate memory against highly similar existing memories.
        Returns a tuple of (RelationType, TargetExistingMemoryID or None)
        """
        if not existing_memories:
            return MemoryRelation.NEW, None

        # Format existing memories for the prompt
        existing_formatted = []
        for em in existing_memories:
            # em could be a Memory object from DB
            existing_formatted.append(f"ID: {em.id} | Type: {em.type} | Entity: {em.entity} | Polarity: {em.polarity} | Content: {em.content}")
        
        existing_text = "\n".join(existing_formatted)
        candidate_text = f"Type: {candidate.get('type')} | Entity: {candidate.get('entity')} | Polarity: {candidate.get('polarity')} | Content: {candidate.get('content')}"

        prompt = f"""
You are the Memory Validator for an AI Companion.
Your task is to compare a new Candidate Memory against a list of Existing Memories.

Candidate Memory:
{candidate_text}

Existing Memories:
{existing_text}

Determine the relationship between the Candidate and the most relevant Existing Memory (if any).
Relationships:
- DUPLICATE: Exactly the same fact.
- CONTRADICTORY: Direct opposite or mutually exclusive fact (e.g. loves X vs hates X).
- COMPLEMENTARY: Both are true and add detail (e.g. loves X + loves Y).
- TEMPORAL_UPDATE: The user changed their mind over time (e.g. used to love X, now loves Y).
- NEW: No strong relation to the existing memories.

Output JSON only:
{{
  "relation": "<ONE OF THE 5 RELATIONSHIPS>",
  "target_memory_id": "<ID of the related existing memory, or null if NEW>"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" },
                temperature=0.0
            )
            
            parsed = json.loads(response.choices[0].message.content)
            relation = parsed.get("relation", MemoryRelation.NEW)
            target_id = parsed.get("target_memory_id", None)
            
            return relation, target_id
        except Exception as e:
            logger.error(f"Failed to validate memory relation: {e}")
            return MemoryRelation.NEW, None
