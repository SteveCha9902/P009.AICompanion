from typing import List
from app.services.context.providers.base import ContextProvider
from app.repositories.message_repository import MessageRepository

class ConversationHistoryProvider(ContextProvider):
    def __init__(self, message_repo: MessageRepository, limit: int = 10):
        self.message_repo = message_repo
        self.limit = limit

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        messages = await self.message_repo.list_by_conversation(conversation_id, limit=self.limit)
        
        # Format for LLM provider (assuming OpenAI style dicts)
        context = []
        for msg in messages:
            context.append({"role": msg.role, "content": msg.content})
        
        return context
