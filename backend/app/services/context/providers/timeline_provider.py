from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.services.timeline.personal_history_engine import PersonalHistoryEngine

class TimelineContextProvider(ContextProvider):
    """
    Life Timeline & Personal History Context Provider:
    Injects temporal event narrative into ContextBuilder prompt.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        result = PersonalHistoryEngine.find_relevant_timeline_narrative(
            user_id=self.user_id,
            user_utterance=current_user_message
        )

        if not result:
            return []

        matched_event, narrative = result
        return [{
            "role": "system",
            "content": f"\n[PERSONAL LIFE TIMELINE & HISTORY NARRATIVE]\n{narrative}\nGuidance: Mention the passage of time or milestone progress naturally and tentatively, without rigid assertions."
        }]
