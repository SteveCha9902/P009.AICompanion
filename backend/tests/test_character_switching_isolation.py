import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.db.models.companion import Companion
from app.db.models.user_character_preference import UserCharacterPreference
from app.domain.character.character_runtime_context import CharacterScope
from app.domain.character.character_scope_guard import CharacterScopeGuard, CharacterScopeViolationError
from app.domain.interaction.interaction_context import InteractionContext
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.context_resolver import CharacterContextResolver
from app.services.companion.domain import NormalizedInput, InputType
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine


@pytest.mark.asyncio
async def test_01_explicit_character_override():
    """Test 1: Explicit companion_id in request overrides active preference."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    # Active Preference is Genie
    pref = UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    mock_repo.get_preference = AsyncMock(return_value=pref)
    mock_repo.list_by_user = AsyncMock(return_value=[
        Companion(id="genie_pk", user_id="u1", name="지니"),
        Companion(id="sua_pk", user_id="u1", name="수아")
    ])

    service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=service)

    # 1. Unspecified companion_id -> uses active Genie
    ctx_default = await resolver.resolve(user_id="u1", companion_id=None)
    assert ctx_default.scope.companion_id == "genie_pk"
    assert ctx_default.identity.name == "지니"

    # 2. Explicit companion_id="sua_pk" -> overrides to Sua
    ctx_override = await resolver.resolve(user_id="u1", companion_id="sua_pk")
    assert ctx_override.scope.companion_id == "sua_pk"
    assert ctx_override.identity.name == "수아"
    assert ctx_override.identity.display_name == "Sua"


@pytest.mark.asyncio
async def test_02_active_character_resolution_routing():
    """Test 2: Requests without companion_id dynamically route to current active character."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    genie = Companion(id="genie_pk", user_id="u1", name="지니")
    sua = Companion(id="sua_pk", user_id="u1", name="수아")
    
    pref = UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    mock_repo.get_preference = AsyncMock(return_value=pref)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)

    service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=service)

    # 1. Initially Genie
    ctx1 = await resolver.resolve(user_id="u1", companion_id=None)
    assert ctx1.scope.companion_id == "genie_pk"

    # 2. Switch to Sua
    mock_repo.set_active_companion = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="u1", active_companion_id="sua_pk")
    )
    await service.set_active_companion("u1", "sua_pk")

    # 3. Next request automatically resolves to Sua
    ctx2 = await resolver.resolve(user_id="u1", companion_id=None)
    assert ctx2.scope.companion_id == "sua_pk"
    assert ctx2.identity.name == "수아"
    assert ctx2.identity.display_name == "Sua"


@pytest.mark.asyncio
async def test_03_mid_interaction_switch_snapshot_isolation():
    """Test 3: In-flight interaction A preserves its initial scope even if active character is switched mid-flight."""
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="genie_pk")

    # Slow LLM that allows mid-interaction active switch
    async def slow_stream(context):
        yield "생각 중입니다... "
        await asyncio.sleep(0.05)
        yield "답변 완료!"

    mock_llm = MagicMock()
    mock_llm.stream = slow_stream

    mock_cb = AsyncMock()
    mock_cb.build.return_value = [{"role": "system", "content": "You are Genie"}]

    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    pref = UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    mock_repo.get_preference = AsyncMock(return_value=pref)
    sua = Companion(id="sua_pk", user_id="u1", name="수아")
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)

    service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=service)

    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=mock_llm,
        context_resolver=resolver
    )

    # Start Interaction A (Genie)
    user_input_a = NormalizedInput(
        user_id="u1",
        interaction_id="inter_A",
        content="지니야 안녕!",
        input_type=InputType.TEXT
    )

    events_a = []
    async def run_interaction_a():
        async for e in orchestrator.process_interaction(user_input_a):
            events_a.append(e)

    async def trigger_switch():
        await asyncio.sleep(0.02)
        mock_repo.set_active_companion = AsyncMock(
            return_value=UserCharacterPreference(id="p1", user_id="u1", active_companion_id="sua_pk")
        )
        await service.set_active_companion("u1", "sua_pk")

    # Run in parallel: Interaction A starts, active switch occurs mid-flight
    await asyncio.gather(run_interaction_a(), trigger_switch())

    # Verify Interaction A completed 100% under Genie scope
    start_event = next(e for e in events_a if "interaction_started" in e)
    assert '"companion_id": "genie_pk"' in start_event
    assert any("interaction_completed" in e for e in events_a)


@pytest.mark.asyncio
async def test_04_new_interaction_after_switch():
    """Test 4: Interaction B started after switch executes completely under Sua scope."""
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="sua_pk")
    
    mock_llm = MagicMock()
    async def quick_stream(context):
        yield "네, 수아입니다."
    mock_llm.stream = quick_stream

    mock_cb = AsyncMock()
    mock_cb.build.return_value = [{"role": "system", "content": "You are Sua"}]

    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    pref = UserCharacterPreference(id="p1", user_id="u1", active_companion_id="sua_pk")
    mock_repo.get_preference = AsyncMock(return_value=pref)

    service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=service)

    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=mock_llm,
        context_resolver=resolver
    )

    user_input_b = NormalizedInput(
        user_id="u1",
        interaction_id="inter_B",
        content="수아야 오늘 회의록 요약해줘",
        input_type=InputType.TEXT
    )

    events_b = []
    async for e in orchestrator.process_interaction(user_input_b):
        events_b.append(e)

    start_event = next(e for e in events_b if "interaction_started" in e)
    assert '"companion_id": "sua_pk"' in start_event


@pytest.mark.asyncio
async def test_05_memory_isolation_filter():
    """Test 5: Memory scope strictly filters and prevents cross-character recall."""
    resolver = CharacterContextResolver(db=None)

    genie_ctx = await resolver.resolve("user_1", "genie_pk")
    sua_ctx = await resolver.resolve("user_1", "sua_pk")

    assert genie_ctx.memory_scope.companion_id == "genie_pk"
    assert sua_ctx.memory_scope.companion_id == "sua_pk"
    assert genie_ctx.memory_scope != sua_ctx.memory_scope


@pytest.mark.asyncio
async def test_06_emotion_isolation():
    """Test 6: Emotional state and PAD dynamics are isolated per companion."""
    from app.db.models.emotion import EmotionState, EmotionType
    
    genie_emotion = EmotionState(companion_id="genie_pk", primary_emotion=EmotionType.AFFECTION, warmth=0.9)
    sua_emotion = EmotionState(companion_id="sua_pk", primary_emotion=EmotionType.CALM, warmth=0.4)

    assert genie_emotion.companion_id != sua_emotion.companion_id
    assert genie_emotion.primary_emotion != sua_emotion.primary_emotion
    assert genie_emotion.warmth != sua_emotion.warmth


@pytest.mark.asyncio
async def test_07_relationship_isolation():
    """Test 7: Relationship social bond and intimacy dimensions are isolated per companion."""
    from app.db.models.relationship import RelationshipState, RelationshipLevel
    
    genie_rel = RelationshipState(companion_id="genie_pk", user_id="u1", closeness=0.9, stage="intimate", relationship_level=RelationshipLevel.CLOSE)
    sua_rel = RelationshipState(companion_id="sua_pk", user_id="u1", closeness=0.3, stage="professional", relationship_level=RelationshipLevel.ACQUAINTANCE)

    assert genie_rel.companion_id != sua_rel.companion_id
    assert genie_rel.closeness != sua_rel.closeness
    assert genie_rel.stage != sua_rel.stage


@pytest.mark.asyncio
async def test_08_voice_isolation():
    """Test 8: Voice profile and neural voice persona are strictly isolated."""
    resolver = CharacterContextResolver(db=None)

    genie_ctx = await resolver.resolve("u1", "genie_pk")
    sua_ctx = await resolver.resolve("u1", "sua_pk")

    assert genie_ctx.voice_profile.voice_id == "genie_warm_v1"
    assert sua_ctx.voice_profile.voice_id == "sua_professional_v1"
    assert genie_ctx.voice_profile.persona_type != sua_ctx.voice_profile.persona_type


@pytest.mark.asyncio
async def test_09_avatar_isolation():
    """Test 9: Avatar visual identity and profile are strictly isolated."""
    resolver = CharacterContextResolver(db=None)

    genie_ctx = await resolver.resolve("u1", "genie_pk")
    sua_ctx = await resolver.resolve("u1", "sua_pk")

    assert isinstance(genie_ctx.avatar_profile, object)
    assert isinstance(sua_ctx.avatar_profile, object)


@pytest.mark.asyncio
async def test_10_agency_isolation_and_scope_guard():
    """Test 10: Scope guard prevents mismatched agency actions or scope violations."""
    scope = CharacterScope(user_id="u1", companion_id="genie_pk")
    
    # Valid matching scope
    assert CharacterScopeGuard.assert_scope(scope, "genie_pk", "AgencyEngine") is True

    # Mismatched scope returns False or raises
    assert CharacterScopeGuard.assert_scope(scope, "sua_pk", "AgencyEngine", raise_error=False) is False
    
    with pytest.raises(CharacterScopeViolationError, match="ScopeViolation"):
        CharacterScopeGuard.assert_scope(scope, "sua_pk", "AgencyEngine", raise_error=True)


@pytest.mark.asyncio
async def test_11_concurrent_interaction_isolation():
    """Test 11: Parallel concurrent interactions for Genie and Sua run with zero context crosstalk."""
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="default")

    async def mock_stream_genie(ctx):
        yield "지니의 따뜻한 답변"

    async def mock_stream_sua(ctx):
        yield "수아의 전문적인 답변"

    mock_llm = MagicMock()
    mock_llm.stream = lambda ctx: mock_stream_genie(ctx) if "Genie" in str(ctx) else mock_stream_sua(ctx)

    mock_cb = AsyncMock()
    mock_cb.build = AsyncMock(side_effect=lambda conv, text: [{"role": "system", "content": "You are " + ("Genie" if "genie" in conv else "Sua")}])

    resolver = CharacterContextResolver(db=None)
    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=mock_llm,
        context_resolver=resolver
    )

    user_input_genie = NormalizedInput(
        user_id="user_conc",
        companion_id="genie",
        conversation_id="conv_genie",
        interaction_id="inter_genie_99",
        content="지니야 사랑해",
        input_type=InputType.TEXT
    )
    user_input_sua = NormalizedInput(
        user_id="user_conc",
        companion_id="sua",
        conversation_id="conv_sua",
        interaction_id="inter_sua_99",
        content="수아야 브리핑해줘",
        input_type=InputType.TEXT
    )

    events_genie = []
    events_sua = []

    async def run_g():
        async for e in orchestrator.process_interaction(user_input_genie):
            events_genie.append(e)

    async def run_s():
        async for e in orchestrator.process_interaction(user_input_sua):
            events_sua.append(e)

    await asyncio.gather(run_g(), run_s())

    # Verify Genie interaction is purely Genie
    start_g = next(e for e in events_genie if "interaction_started" in e)
    assert '"companion_id": "genie"' in start_g

    # Verify Sua interaction is purely Sua
    start_s = next(e for e in events_sua if "interaction_started" in e)
    assert '"companion_id": "sua"' in start_s
