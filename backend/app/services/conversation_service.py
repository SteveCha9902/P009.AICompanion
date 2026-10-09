import asyncio
import time
from typing import AsyncGenerator
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.context.builder import ContextBuilder
from app.services.llm.base import BaseLLMProvider
from app.services.persona_service import PersonaService
from app.services.emotion_service import EmotionService
import uuid

class ConversationService:
    def __init__(
        self, 
        db_session: AsyncSession,
        context_builder: ContextBuilder,
        llm_provider: BaseLLMProvider,
        persona_service: PersonaService,
        emotion_service: EmotionService = None
    ):
        self.db = db_session
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.persona_service = persona_service
        self.emotion_service = emotion_service
        self.msg_repo = MessageRepository(self.db)
        self.conv_repo = ConversationRepository(self.db)

    async def get_or_create_conversation(self, user_id: str, conversation_id: str = None) -> str:
        if conversation_id:
            has_ownership = await self.conv_repo.check_ownership(conversation_id, user_id)
            if not has_ownership:
                raise HTTPException(status_code=403, detail="Forbidden")
            return conversation_id
        
        conv = await self.conv_repo.create(user_id=user_id, title="New Conversation")
        return conv.id

    async def send_message_stream(
        self, 
        user_id: str, 
        conversation_id: str, 
        content: str, 
        request_id: str
    ) -> AsyncGenerator[str, None]:
        
        start_time = time.time()
        
        # Get persona version
        persona = await self.persona_service.get_or_create_persona(user_id)
        persona_version = persona.version

        # 1. Save User Message
        msg = await self.msg_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=content,
            metadata={"request_id": request_id}
        )
        
        # 1. Fetch recent history
        history = await self.msg_repo.list_by_conversation(conversation_id, limit=5)
        history.reverse()
        history_dict = [{"role": m.role, "content": m.content} for m in history]
        
        # 2. Process Emotion Synchronously
        if self.emotion_service:
            try:
                await self.emotion_service.process_user_message(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_id=msg.id,
                    current_message=content,
                    history=history_dict
                )
            except Exception as e:
                # Failure isolation
                print(f"Emotion processing failed: {e}")
        
        # 3. Build Context
        context = await self.context_builder.build(conversation_id, content)

        # 4. Stream from LLM
        full_content = ""
        model_used = ""
        ttft = None

        try:
            async for chunk in self.llm_provider.stream(context):
                if not ttft:
                    ttft = time.time() - start_time
                
                full_content += chunk.content
                if chunk.model:
                    model_used = chunk.model
                
                # Yield SSE format
                yield f"data: {chunk.content}\n\n"

        except asyncio.CancelledError:
            # Client disconnected early, we still save what we have
            pass
        except Exception as e:
            # LLM error, we might want to save an error message or just pass
            yield f"data: [ERROR] {str(e)}\n\n"
            raise e
        finally:
            # 4. Save Assistant Message
            total_latency = time.time() - start_time
            await self.msg_repo.create(
                conversation_id=conversation_id,
                role="assistant",
                content=full_content,
                metadata={
                    "request_id": request_id,
                    "model": model_used,
                    "ttft": ttft,
                    "total_latency": total_latency,
                    "status": "completed" if full_content else "interrupted",
                    "persona_version": persona_version
                }
            )
            # 5. Trigger Memory Extraction as background task (fire and forget)
            # In FastAPI streaming, we can't easily use BackgroundTasks within the generator,
            # so we'll launch an asyncio task directly.
            asyncio.create_task(self._extract_memory_bg(user_id, conversation_id))
            
            # End stream marker
            yield "data: [DONE]\n\n"

    async def _extract_memory_bg(self, user_id: str, conversation_id: str):
        # Local import to avoid circular dependency or large context loads
        from app.db.session import async_session
        from app.services.memory_service import MemoryService
        from app.repositories.memory_repository import MemoryRepository
        from app.repositories.companion_repository import CompanionRepository
        from app.services.memory.extractor import MemoryExtractor
        from app.services.memory.validator import MemoryValidator
        from app.services.memory.embedding import OpenAIEmbeddingProvider
        
        async with async_session() as session:
            memory_repo = MemoryRepository(session)
            companion_repo = CompanionRepository(session)
            msg_repo = MessageRepository(session)
            embedding_provider = OpenAIEmbeddingProvider()
            extractor = MemoryExtractor()
            validator = MemoryValidator()
            
            service = MemoryService(
                session, memory_repo, companion_repo, msg_repo,
                embedding_provider, extractor, validator
            )
            await service.process_conversation_for_memory(user_id, conversation_id)

