import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.domain.character.character_runtime_context import (
    CharacterScope,
    CharacterMemoryScope,
    CharacterAvatarProfile,
    CharacterRuntimeContext,
    CharacterRuntimeState,
)
from app.services.character.context_resolver import (
    CharacterContextResolver,
    DEFAULT_COMPANION_ID,
)
from app.services.companion.domain import NormalizedInput, InputType, SSEEventType
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine


@pytest.mark.asyncio
async def test_01_default_character_resolution():
    """Test 1: Default Character Resolution maps None to Genie runtime context."""
    resolver = CharacterContextResolver(db=None)
    ctx = await resolver.resolve(user_id="user_123", companion_id=None)

    assert isinstance(ctx, CharacterRuntimeContext)
    assert ctx.scope.user_id == "user_123"
    assert ctx.scope.companion_id == DEFAULT_COMPANION_ID
    assert ctx.scope.character_id == DEFAULT_COMPANION_ID
    assert ctx.identity.name == "지니"
    assert ctx.identity.display_name == "Genie"
    assert ctx.voice_profile.voice_id == "genie_warm_v1"
    assert ctx.memory_scope.companion_id == DEFAULT_COMPANION_ID


@pytest.mark.asyncio
async def test_02_explicit_character_resolution():
    """Test 2: Explicit Character Resolution for a named companion (e.g. Sua)."""
    resolver = CharacterContextResolver(db=None)
    ctx = await resolver.resolve(user_id="user_123", companion_id="sua")

    assert ctx.scope.user_id == "user_123"
    assert ctx.scope.companion_id == "sua"
    assert ctx.scope.character_id == "sua"
    assert ctx.identity.name == "수아"
    assert ctx.identity.display_name == "Sua"
    assert "sua" in ctx.voice_profile.voice_id
    assert ctx.memory_scope.companion_id == "sua"


@pytest.mark.asyncio
async def test_03_backward_compatibility_orchestrator():
    """Test 3: Backward compatibility of CompanionOrchestrator with legacy calls."""
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="default_companion")
    
    mock_cb = AsyncMock()
    mock_cb.build.return_value = [{"role": "system", "content": "You are Genie"}]
    
    mock_llm = MagicMock()
    async def mock_stream(context):
        yield "안녕하세요! 저는 지니예요."
    mock_llm.stream = mock_stream

    resolver = CharacterContextResolver(db=None)
    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=mock_llm,
        context_resolver=resolver
    )

    # Call with companion_id=None (legacy style)
    user_input = NormalizedInput(
        user_id="legacy_user",
        conversation_id="conv_legacy",
        content="안녕!",
        input_type=InputType.TEXT
    )

    events = []
    async for event_str in orchestrator.process_interaction(user_input):
        events.append(event_str)

    assert len(events) > 0
    assert any("interaction_started" in e for e in events)
    assert any("interaction_completed" in e for e in events)


@pytest.mark.asyncio
async def test_04_scope_propagation():
    """Test 4: Scope propagation guarantees canonical companion_id throughout pipeline."""
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="sua")
    
    mock_cb = AsyncMock()
    mock_cb.build.return_value = [{"role": "system", "content": "You are Sua"}]
    
    mock_llm = MagicMock()
    async def mock_stream(context):
        yield "네, 비서 수아입니다."
    mock_llm.stream = mock_stream

    resolver = CharacterContextResolver(db=None)
    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=mock_llm,
        context_resolver=resolver
    )

    user_input = NormalizedInput(
        user_id="user_abc",
        companion_id="sua",
        conversation_id="conv_sua",
        content="오늘 일정 알려줘",
        input_type=InputType.TEXT
    )

    start_event_found = False
    async for event_str in orchestrator.process_interaction(user_input):
        if "interaction_started" in event_str:
            assert '"companion_id": "sua"' in event_str
            start_event_found = True

    assert start_event_found is True


@pytest.mark.asyncio
async def test_05_context_isolation():
    """Test 5: Strict Context Isolation between Genie and Sua contexts."""
    resolver = CharacterContextResolver(db=None)

    genie_ctx = await resolver.resolve(user_id="user_1", companion_id=None)
    sua_ctx = await resolver.resolve(user_id="user_1", companion_id="sua")

    assert genie_ctx.scope != sua_ctx.scope
    assert genie_ctx.scope.companion_id != sua_ctx.scope.companion_id
    assert genie_ctx.identity.name != sua_ctx.identity.name
    assert genie_ctx.voice_profile.voice_id != sua_ctx.voice_profile.voice_id
    assert genie_ctx.memory_scope.companion_id != sua_ctx.memory_scope.companion_id


@pytest.mark.asyncio
async def test_06_no_character_context_leakage():
    """Test 6: Sequential calls do not leak character identity across resolutions."""
    resolver = CharacterContextResolver(db=None)

    ctx1 = await resolver.resolve(user_id="user_A", companion_id="genie")
    ctx2 = await resolver.resolve(user_id="user_A", companion_id="hana")
    ctx3 = await resolver.resolve(user_id="user_A", companion_id="genie")

    assert ctx1.identity.name == "지니"
    assert ctx2.identity.name == "하나"
    assert ctx2.identity.display_name == "Hana"
    assert ctx3.identity.name == "지니"
    assert ctx2.voice_profile.voice_id != ctx3.voice_profile.voice_id


@pytest.mark.asyncio
async def test_07_resolver_cache_isolation():
    """Test 7: Cache isolation ensures composite key (user_id, companion_id) separation."""
    resolver = CharacterContextResolver(db=None)

    # Same companion, different users
    ctx_u1 = await resolver.resolve(user_id="user_1", companion_id="genie")
    ctx_u2 = await resolver.resolve(user_id="user_2", companion_id="genie")

    assert ctx_u1.scope.user_id == "user_1"
    assert ctx_u2.scope.user_id == "user_2"
    assert len(resolver._cache) == 2

    # Same user, different companions
    ctx_u1_sua = await resolver.resolve(user_id="user_1", companion_id="sua")
    assert len(resolver._cache) == 3
    assert ("user_1", "genie") in resolver._cache
    assert ("user_1", "sua") in resolver._cache
    assert ("user_2", "genie") in resolver._cache


@pytest.mark.asyncio
async def test_08_default_resolution_stability():
    """Test 8: Default resolution stability across various blank / default representations."""
    resolver = CharacterContextResolver(db=None)

    ctx_none = await resolver.resolve(user_id="u1", companion_id=None)
    ctx_empty = await resolver.resolve(user_id="u1", companion_id="")
    ctx_def = await resolver.resolve(user_id="u1", companion_id="default")

    assert ctx_none.scope.companion_id == DEFAULT_COMPANION_ID
    assert ctx_empty.scope.companion_id == DEFAULT_COMPANION_ID
    assert ctx_def.scope.companion_id == DEFAULT_COMPANION_ID
    assert ctx_none.identity.name == "지니"
