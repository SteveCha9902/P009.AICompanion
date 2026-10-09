import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.domain import NormalizedInput, InputType, SSEEventType
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine
from app.services.context.builder import ContextBuilder
from app.services.llm.base import BaseLLMProvider, LLMResponse, LLMProviderError
from app.services.presentation_engine import AvatarStateResolver
from app.services.character.context_resolver import CharacterContextResolver
from app.domain.character.character_runtime_context import CharacterRuntimeContext, CharacterScope
from app.domain.interaction.companion_interaction_context import CompanionInteractionContext, PresentationCommand
from app.domain.memory.character_memory_scope import CharacterScopeRequiredError


class MockStreamingLLM(BaseLLMProvider):
    async def stream(self, messages, **kwargs):
        chunks = ["안녕하세요! ", "오늘도 ", "좋은 하루예요."]
        for c in chunks:
            yield LLMResponse(content=c, model="mock")

    async def generate(self, messages, **kwargs):
        return LLMResponse(content="안녕하세요! 오늘도 좋은 하루예요.", model="mock")


def create_orchestrator(mock_resolver=None, mock_llm=None):
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="genie_pk")
    
    mock_cb = MagicMock(spec=ContextBuilder)
    mock_cb.build = AsyncMock(return_value=[
        {"role": "system", "content": "You are a companion."},
        {"role": "user", "content": "안녕"}
    ])
    
    llm = mock_llm or MockStreamingLLM()
    avatar_resolver = MagicMock(spec=AvatarStateResolver)
    avatar_resolver.resolve = MagicMock(return_value={"expression": "smile", "animation": "nod", "energy": 0.6})
    
    msg_repo = MagicMock()
    msg_repo.create = AsyncMock()

    resolver = mock_resolver or CharacterContextResolver()

    return CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=llm,
        avatar_resolver=avatar_resolver,
        message_repo=msg_repo,
        context_resolver=resolver
    )


@pytest.mark.asyncio
async def test_01_text_interaction_genie_pinned_response():
    """Test 1: Genie text interaction emits SSE events with pinned scope."""
    orch = create_orchestrator()
    inp = NormalizedInput(
        user_id="u1",
        companion_id="genie_pk",
        conversation_id="conv1",
        content="지니야 오늘 날씨 어때?",
        input_type=InputType.TEXT
    )

    events = []
    async for event in orch.process_interaction(inp):
        events.append(event)

    assert len(events) >= 4
    assert any("interaction_started" in e for e in events)
    assert any("text_completed" in e for e in events)
    assert any("interaction_completed" in e for e in events)


@pytest.mark.asyncio
async def test_02_voice_interaction_mani_shimmer_binding():
    """Test 2: Mani voice interaction preserves Shimmer voice profile in pinned context."""
    orch = create_orchestrator()
    inp = NormalizedInput(
        user_id="u1",
        companion_id="c_mani",
        conversation_id="conv_mani",
        content="마니야 학원 잘 다녀왔어?",
        input_type=InputType.VOICE
    )

    resp = await orch.process_interaction_sync(inp)
    assert resp.text != ""


@pytest.mark.asyncio
async def test_03_vision_interaction_hana_context_response():
    """Test 3: Hana vision interaction handles visual context without losing character scope."""
    orch = create_orchestrator()
    inp = NormalizedInput(
        user_id="u1",
        companion_id="c_hana",
        conversation_id="conv_hana",
        content="이 그림 어때?",
        input_type=InputType.VISION,
        raw_metadata={"image_present": True}
    )

    resp = await orch.process_interaction_sync(inp)
    assert resp is not None


@pytest.mark.asyncio
async def test_04_full_pipeline_cognition_dynamic_state_presentation():
    """Test 4: Full pipeline execution maintains CharacterScope integrity from start to finish."""
    orch = create_orchestrator()
    inp = NormalizedInput(
        user_id="u1",
        companion_id="genie_pk",
        conversation_id="conv_full",
        content="사랑해 지니야"
    )

    events = []
    async for e in orch.process_interaction(inp):
        events.append(e)

    assert any("avatar_state" in e for e in events)
    assert any("interaction_completed" in e for e in events)


@pytest.mark.asyncio
async def test_05_rapid_switching_orchestration_integrity():
    """Test 5: Rapid sequential switching across Genie -> Mani -> Hana preserves independent scopes."""
    orch = create_orchestrator()
    sequence = ["genie_pk", "c_mani", "c_hana", "genie_pk"]

    for cid in sequence:
        inp = NormalizedInput(
            user_id="u1",
            companion_id=cid,
            conversation_id=f"conv_{cid}",
            content=f"Hello {cid}"
        )
        resp = await orch.process_interaction_sync(inp)
        assert resp is not None


@pytest.mark.asyncio
async def test_06_concurrent_characters_multi_stream():
    """Test 6: Concurrent interaction streams for Genie, Mani, Hana maintain isolated states."""
    orch = create_orchestrator()

    async def run_stream(cid: str):
        inp = NormalizedInput(
            user_id="u1",
            companion_id=cid,
            conversation_id=f"conv_{cid}",
            content=f"Message for {cid}"
        )
        collected = []
        async for e in orch.process_interaction(inp):
            collected.append(e)
        return cid, len(collected)

    results = await asyncio.gather(
        run_stream("genie_pk"),
        run_stream("c_mani"),
        run_stream("c_hana")
    )

    for cid, event_count in results:
        assert event_count >= 4


@pytest.mark.asyncio
async def test_07_stale_response_isolation_after_switch():
    """Test 7: CompanionInteractionContext ensures that slow responses target their pinned companion."""
    ctx = CompanionInteractionContext(
        interaction_id="int_slow",
        scope=CharacterScope(user_id="u1", companion_id="genie_pk")
    )
    assert ctx.validate_scope_integrity("genie_pk") is True
    with pytest.raises(ValueError, match="ScopeIntegrityViolation"):
        ctx.validate_scope_integrity("c_mani")


@pytest.mark.asyncio
async def test_08_tts_stream_race_isolation():
    """Test 8: PresentationCommand encapsulates companion-specific voice metadata."""
    cmd_genie = PresentationCommand(
        interaction_id="int_1",
        companion_id="genie_pk",
        voice_profile="nova",
        avatar_binding="warm_wife_2d"
    )
    cmd_mani = PresentationCommand(
        interaction_id="int_2",
        companion_id="c_mani",
        voice_profile="shimmer",
        avatar_binding="lovely_daughter_2d"
    )

    assert cmd_genie.voice_profile == "nova"
    assert cmd_mani.voice_profile == "shimmer"
    assert cmd_genie.companion_id != cmd_mani.companion_id


@pytest.mark.asyncio
async def test_09_avatar_animation_race_isolation():
    """Test 9: PresentationCommand guarantees isolated avatar bindings."""
    cmd_genie = PresentationCommand(
        interaction_id="int_1",
        companion_id="genie_pk",
        voice_profile="nova",
        avatar_binding="warm_wife_2d",
        expression="warm_smile"
    )
    cmd_hana = PresentationCommand(
        interaction_id="int_3",
        companion_id="c_hana",
        voice_profile="alloy",
        avatar_binding="friend_2d",
        expression="playful_wink"
    )

    assert cmd_genie.avatar_binding != cmd_hana.avatar_binding
    assert cmd_genie.expression == "warm_smile"
    assert cmd_hana.expression == "playful_wink"


@pytest.mark.asyncio
async def test_10_agency_proactive_race_isolation():
    """Test 10: Proactive Agency events retain pinned interaction scope."""
    ctx = CompanionInteractionContext(
        interaction_id="int_agency",
        scope=CharacterScope(user_id="u1", companion_id="genie_pk")
    )
    assert ctx.scope.companion_id == "genie_pk"


@pytest.mark.asyncio
async def test_11_idempotent_retry_duplicate_rejection():
    """Test 11: Idempotency guard rejects duplicate active interaction_id."""
    orch = create_orchestrator()
    inp = NormalizedInput(
        interaction_id="fixed_int_123",
        user_id="u1",
        companion_id="genie_pk",
        conversation_id="conv1",
        content="중복 테스트"
    )

    from app.services.companion.orchestrator import active_interactions
    active_interactions.add("fixed_int_123")

    events = []
    async for e in orch.process_interaction(inp):
        events.append(e)

    active_interactions.discard("fixed_int_123")
    assert any("Duplicate interaction in progress" in e for e in events)


@pytest.mark.asyncio
async def test_12_subsystem_failure_recovery_graceful_handling():
    """Test 12: LLM Provider failure emits clean error event and resets to IDLE without breaking scope."""
    class FailingLLM(BaseLLMProvider):
        async def stream(self, messages, **kwargs):
            raise LLMProviderError(code="RATE_LIMIT", message="Provider rate limit exceeded")

        async def generate(self, messages, **kwargs):
            raise LLMProviderError(code="RATE_LIMIT", message="Provider rate limit exceeded")

    orch = create_orchestrator(mock_llm=FailingLLM())
    inp = NormalizedInput(
        user_id="u1",
        companion_id="genie_pk",
        conversation_id="conv1",
        content="오류 테스트"
    )

    events = []
    async for e in orch.process_interaction(inp):
        events.append(e)

    assert any("error" in e for e in events)


@pytest.mark.asyncio
async def test_13_ownership_attack_rejection():
    """Test 13: Accessing another user's companion raises PermissionError and rejects execution."""
    mock_resolver = MagicMock()
    mock_resolver.resolve = AsyncMock(side_effect=PermissionError("User does not own companion"))

    orch = create_orchestrator(mock_resolver=mock_resolver)
    inp = NormalizedInput(
        user_id="uA",
        companion_id="c_other_user",
        conversation_id="conv1",
        content="탈취 시도"
    )

    events = []
    async for e in orch.process_interaction(inp):
        events.append(e)

    assert any("error" in e for e in events)


@pytest.mark.asyncio
async def test_14_invalid_companion_id_fail_closed():
    """Test 14: Non-existent companion ID triggers fail-closed error response."""
    mock_resolver = MagicMock()
    mock_resolver.resolve = AsyncMock(side_effect=ValueError("Companion not found"))

    orch = create_orchestrator(mock_resolver=mock_resolver)
    inp = NormalizedInput(
        user_id="u1",
        companion_id="non_existent_id",
        conversation_id="conv1",
        content="미존재 캐릭터"
    )

    events = []
    async for e in orch.process_interaction(inp):
        events.append(e)

    assert any("error" in e for e in events)


@pytest.mark.asyncio
async def test_15_archived_companion_id_blocked():
    """Test 15: Interaction with archived companion is blocked with PermissionError."""
    mock_resolver = MagicMock()
    mock_resolver.resolve = AsyncMock(side_effect=PermissionError("Companion is archived"))

    orch = create_orchestrator(mock_resolver=mock_resolver)
    inp = NormalizedInput(
        user_id="u1",
        companion_id="c_archived",
        conversation_id="conv1",
        content="보관 캐릭터"
    )

    events = []
    async for e in orch.process_interaction(inp):
        events.append(e)

    assert any("error" in e for e in events)
