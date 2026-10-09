import logging
import asyncio
from typing import Optional
from enum import Enum
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine
from app.services.context.builder import ContextBuilder

# 8 Context Providers
from app.services.context.providers.character_identity import CharacterIdentityProvider
from app.services.context.providers.persona_provider import PersonaContextProvider
from app.services.context.providers.relationship_provider import RelationshipContextProvider
from app.services.context.providers.emotion_provider import EmotionContextProvider
from app.services.context.providers.memory_provider import MemoryContextProvider
from app.services.context.providers.presence_provider import PresenceContextProvider
from app.services.context.providers.vision_context import VisionContextProvider
from app.services.context.providers.conversation_history import ConversationHistoryProvider


# Repositories & Services
from app.repositories.companion_repository import CompanionRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.emotion_repository import EmotionRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.presence_repository import PresenceRepository
from app.db.models.presence import PresenceState, PresenceStateEnum

from app.services.persona_service import PersonaService
from app.services.emotion_service import EmotionService
from app.services.emotion.extractor import EmotionExtractor
from app.services.emotion.transition import TransitionEngine
from app.services.emotion.decay import DecayEngine as EmotionDecayEngine
from app.services.relationship_service import RelationshipService
from app.services.relationship.policy import PolicyEngine, BehaviorPolicy
from app.services.relationship.decay import DecayEngine as RelDecayEngine
from app.services.memory.retriever import MemoryRetriever
from app.services.presentation_engine import AvatarStateResolver
from app.services.providers.factory import ProviderFactory

logger = logging.getLogger(__name__)

# Global Event Bus instance
global_event_bus = CompanionEventBus()

class RuntimeState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    DRAINING = "DRAINING"
    STOPPED = "STOPPED"

class CompanionRuntimeLifecycle:
    """
    Manages the lifecycle of the Companion Runtime to prevent multiple instantiations and leaks.
    """
    def __init__(self):
        self.state = RuntimeState.CREATED

    def initialize(self):
        self.state = RuntimeState.INITIALIZING
        logger.info("[RuntimeLifecycle] Initializing Companion Runtime...")
        # Initialization logic (connection pools, warmup)
        self.state = RuntimeState.READY
        logger.info("[RuntimeLifecycle] Companion Runtime is READY.")

    def start(self):
        self.state = RuntimeState.RUNNING
        logger.info("[RuntimeLifecycle] Companion Runtime is RUNNING.")

    def stop(self):
        self.state = RuntimeState.DRAINING
        logger.info("[RuntimeLifecycle] Companion Runtime is DRAINING...")
        # Cleanup
        self.state = RuntimeState.STOPPED
        logger.info("[RuntimeLifecycle] Companion Runtime is STOPPED.")

runtime_lifecycle = CompanionRuntimeLifecycle()

async def create_companion_orchestrator(
    db: AsyncSession,
    user_id: str,
    companion_id: str = "default_companion",
    llm_provider = None
) -> CompanionOrchestrator:
    """
    Composition Root: Assembles 7 Context Providers, StateMachine, Avatar Resolver, and EventBus.
    Uses ProviderFactory to resolve independent Providers without hardcoded coupling.
    """
    companion_repo = CompanionRepository(db)
    msg_repo = MessageRepository(db)
    persona_repo = PersonaRepository(db)
    memory_repo = MemoryRepository(db)
    emotion_repo = EmotionRepository(db)
    rel_repo = RelationshipRepository(db)
    presence_repo = PresenceRepository(db)

    # 1. Services
    persona_service = PersonaService(db)
    
    emotion_service = EmotionService(
        session=db,
        emotion_repo=emotion_repo,
        companion_repo=companion_repo,
        persona_repo=persona_repo,
        extractor=EmotionExtractor(),
        transition_engine=TransitionEngine(),
        decay_engine=EmotionDecayEngine()
    )
    
    relationship_service = RelationshipService(
        session=db,
        relationship_repo=rel_repo,
        policy_engine=PolicyEngine(),
        behavior_policy=BehaviorPolicy(),
        decay_engine=RelDecayEngine()
    )
    
    embedding_provider = ProviderFactory.get_embedding_provider()
    memory_retriever = MemoryRetriever(memory_repo, embedding_provider)

    # 2. Presence State
    current_presence = None
    try:
        res = presence_repo.get_state(companion_id)
        current_presence = await res if asyncio.iscoroutine(res) or hasattr(res, "__await__") else res
    except Exception:
        current_presence = None
        
    if current_presence is None:
        current_presence = PresenceState(companion_id=companion_id, state=PresenceStateEnum.AVAILABLE)
    
    # 3. 8 Context Providers
    p0_character = CharacterIdentityProvider(db=db, companion_id=companion_id)
    p1_persona = PersonaContextProvider(persona_service, user_id=user_id)
    p2_relationship = RelationshipContextProvider(relationship_service, companion_repo, user_id=user_id, db=db)

    p3_emotion = EmotionContextProvider(emotion_service, companion_repo, user_id=user_id)
    p4_memory = MemoryContextProvider(memory_retriever, companion_repo, user_id=user_id, db=db)

    p5_presence = PresenceContextProvider(presence_state=current_presence)
    p6_vision = VisionContextProvider(db=db)
    p7_history = ConversationHistoryProvider(msg_repo, limit=10)
    from app.services.reflection.providers.reflection_provider import ReflectionContextProvider
    p8_reflection = ReflectionContextProvider(db=db, companion_id=companion_id)

    context_builder = ContextBuilder(providers=[
        p0_character,
        p1_persona,
        p2_relationship,
        p3_emotion,
        p4_memory,
        p5_presence,
        p6_vision,
        p7_history,
        p8_reflection
    ])




    # 4. State Machine, Avatar Resolver & Character Context Resolver (SB-1 & SB-2)
    from app.services.character.context_resolver import CharacterContextResolver
    from app.repositories.character_registry_repository import CharacterRegistryRepository
    from app.services.character.registry_service import CharacterRegistryService
    
    registry_repo = CharacterRegistryRepository(db)
    registry_service = CharacterRegistryService(repository=registry_repo, db_session=db)
    
    state_machine = InteractionStateMachine(companion_id=companion_id)
    avatar_resolver = AvatarStateResolver(db=db)
    context_resolver = CharacterContextResolver(db=db, registry_service=registry_service)
    
    # 5. Pluggable LLM Provider via ProviderFactory
    if llm_provider is None:
        llm_provider = ProviderFactory.get_llm_provider()

    orchestrator = CompanionOrchestrator(
        event_bus=global_event_bus,
        state_machine=state_machine,
        context_builder=context_builder,
        llm_provider=llm_provider,
        avatar_resolver=avatar_resolver,
        message_repo=msg_repo,
        context_resolver=context_resolver
    )

    return orchestrator

async def get_companion_orchestrator(
    x_user_id: Optional[str] = Header(default="default_user"),
    db: AsyncSession = Depends(get_db)
) -> CompanionOrchestrator:
    """
    FastAPI Dependency for CompanionOrchestrator.
    """
    return await create_companion_orchestrator(
        db=db,
        user_id=x_user_id
    )
