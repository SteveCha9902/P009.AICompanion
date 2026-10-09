from typing import List
from app.services.context.providers.base import ContextProvider
from app.db.models.presence import PresenceState, PresenceStateEnum
import logging

logger = logging.getLogger(__name__)

class PresenceContextProvider(ContextProvider):
    def __init__(self, presence_state: PresenceState, proactive_reason: str = None):
        self.presence_state = presence_state
        self.proactive_reason = proactive_reason

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        try:
            if not self.proactive_reason:
                return []

            lines = [
                "[PRESENCE & PROACTIVE CONTEXT]",
                f"The companion's current presence state is {self.presence_state.state.value if hasattr(self.presence_state.state, 'value') else self.presence_state.state}.",
                "You are initiating this conversation PROACTIVELY because:",
                f"- {self.proactive_reason}",
                "",
                "INSTRUCTION: Use this context to naturally initiate the conversation. Do not act like the user just asked you a question. Acknowledge the reason for your proactive message naturally based on your persona."
            ]

            formatted_presence = "\n".join(lines)

            return [
                {
                    "role": "system",
                    "content": formatted_presence
                }
            ]
        except Exception as e:
            logger.error(f"Failed to build presence context: {e}")
            return []
