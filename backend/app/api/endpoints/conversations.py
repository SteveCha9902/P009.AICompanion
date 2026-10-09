from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid

from app.db.session import get_db
from app.services.conversation_service import ConversationService
from app.services.context.builder import ContextBuilder
from app.services.context.providers.conversation_history import ConversationHistoryProvider
from app.services.context.providers.persona_provider import PersonaContextProvider
from app.services.context.providers.memory_provider import MemoryContextProvider
from app.services.context.providers.emotion_provider import EmotionContextProvider
from app.services.context.providers.relationship_provider import RelationshipContextProvider
from app.services.llm.openai import OpenAIProvider
from app.services.memory.embedding import OpenAIEmbeddingProvider
from app.services.memory.retriever import MemoryRetriever
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.companion_repository import CompanionRepository
from app.repositories.emotion_repository import EmotionRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.persona_repository import PersonaRepository
from app.services.persona_service import PersonaService
from app.services.emotion_service import EmotionService
from app.services.emotion.extractor import EmotionExtractor
from app.services.emotion.transition import TransitionEngine
from app.services.emotion.decay import DecayEngine
from app.services.relationship_service import RelationshipService
from app.services.relationship.policy import PolicyEngine, BehaviorPolicy
from app.services.relationship.decay import DecayEngine as RelDecayEngine

"""
[LEGACY PATH - ISOLATED]
This endpoint (/conversations) represents the legacy conversation pipeline.
It is maintained for backward compatibility.
Do NOT add new cognitive features here.
All new interactions MUST go through POST /companion/interactions (CompanionOrchestrator).
"""
router = APIRouter(tags=["Legacy Conversations"])

class SendMessageRequest(BaseModel):
    content: str

def get_conversation_service(x_user_id: str = Header(...), db: AsyncSession = Depends(get_db)):
    msg_repo = MessageRepository(db)
    history_provider = ConversationHistoryProvider(msg_repo, limit=10)
    
    companion_repo = CompanionRepository(db)
    
    persona_repo = PersonaRepository(db)
    persona_service = PersonaService(db)
    persona_provider = PersonaContextProvider(persona_service, user_id=x_user_id)
    
    memory_repo = MemoryRepository(db)
    embedding_provider = OpenAIEmbeddingProvider()
    memory_retriever = MemoryRetriever(memory_repo, embedding_provider)
    memory_provider = MemoryContextProvider(memory_retriever, companion_repo, user_id=x_user_id)
    
    emotion_repo = EmotionRepository(db)
    extractor = EmotionExtractor()
    transition_engine = TransitionEngine()
    decay_engine = DecayEngine()
    emotion_service = EmotionService(db, emotion_repo, companion_repo, persona_repo, extractor, transition_engine, decay_engine)
    emotion_provider = EmotionContextProvider(emotion_service, companion_repo, user_id=x_user_id)
    
    rel_repo = RelationshipRepository(db)
    rel_policy = PolicyEngine()
    rel_behavior = BehaviorPolicy()
    rel_decay = RelDecayEngine()
    relationship_service = RelationshipService(db, rel_repo, rel_policy, rel_behavior, rel_decay)
    relationship_provider = RelationshipContextProvider(relationship_service, companion_repo, user_id=x_user_id)
    
    # Priority: SYSTEM/SAFETY > PERSONA > MEMORY > EMOTION > RELATIONSHIP > HISTORY > USER INPUT
    context_builder = ContextBuilder(providers=[persona_provider, memory_provider, emotion_provider, relationship_provider, history_provider])
    llm_provider = OpenAIProvider()
    
    return ConversationService(db, context_builder, llm_provider, persona_service, emotion_service)

@router.post("/conversations")
async def create_conversation(
    x_user_id: str = Header(..., description="Temporary auth header for Sprint 2"),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conv = await repo.create(user_id=x_user_id)
    return {"id": conv.id, "title": conv.title}

@router.get("/conversations")
async def list_conversations(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    convs = await repo.list_by_user(user_id=x_user_id)
    return [{"id": c.id, "title": c.title, "updated_at": c.updated_at} for c in convs]

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    if not await repo.check_ownership(conversation_id, x_user_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Forbidden")
    
    msg_repo = MessageRepository(db)
    msgs = await msg_repo.list_by_conversation(conversation_id)
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    body: SendMessageRequest,
    x_user_id: str = Header(...),
    service: ConversationService = Depends(get_conversation_service)
):
    request_id = str(uuid.uuid4())
    
    # Verify ownership and existence
    await service.get_or_create_conversation(user_id=x_user_id, conversation_id=conversation_id)

    # SSE Streaming response
    return StreamingResponse(
        service.send_message_stream(
            user_id=x_user_id,
            conversation_id=conversation_id,
            content=body.content,
            request_id=request_id
        ),
        media_type="text/event-stream"
    )
