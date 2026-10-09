from abc import ABC, abstractmethod
from typing import List
from app.db.models.message import Message

class ContextProvider(ABC):
    @abstractmethod
    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        """
        Returns a list of messages (role, content) to be injected into the LLM context.
        """
        pass
