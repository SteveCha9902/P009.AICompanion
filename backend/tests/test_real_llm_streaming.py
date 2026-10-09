import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine
from app.services.companion.domain import NormalizedInput, InputType, SSEEventType
from app.services.llm.base import BaseLLMProvider, LLMResponse

class FakeStreamingLLM(BaseLLMProvider):
    async def generate(self, messages):
        return LLMResponse(content="안녕하세요!", model="fake-gpt")
    
    async def stream(self, messages):
        tokens = ["안녕", "하세요", "! ", "반가워요", "."]
        for token in tokens:
            yield LLMResponse(content=token, model="fake-gpt")

@pytest.mark.asyncio
async def test_streaming_event_ordering_and_sequence():
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="comp_stream")
    
    mock_context_builder = AsyncMock()
    mock_context_builder.build.return_value = [
        {"role": "system", "content": "You are P009."},
        {"role": "user", "content": "안녕"}
    ]
    
    mock_avatar = MagicMock()
    mock_avatar.resolve.return_value = {"expression": "happy", "animation": "nod", "intensity": 0.8}
    
    mock_message_repo = MagicMock()
    mock_message_repo.save_message = AsyncMock()

    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_context_builder,
        llm_provider=FakeStreamingLLM(),
        avatar_resolver=mock_avatar,
        message_repo=mock_message_repo
    )

    user_input = NormalizedInput(
        interaction_id="INT-STREAM-001",
        user_id="user_stream",
        companion_id="comp_stream",
        conversation_id="conv_stream",
        input_type=InputType.TEXT,
        content="안녕"
    )

    events = []
    async for sse_chunk in orchestrator.process_interaction(user_input):
        lines = [line.strip() for line in sse_chunk.strip().split("\n") if line.strip()]
        event_dict = {}
        for line in lines:
            if line.startswith("id:"):
                event_dict["id"] = line.split(":", 1)[1].strip()
            elif line.startswith("event:"):
                event_dict["event"] = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_dict["data"] = json.loads(line.split(":", 1)[1].strip())
        if event_dict:
            events.append(event_dict)

    # Verify event types and ordering
    event_types = [e["event"] for e in events]
    assert event_types[0] == SSEEventType.INTERACTION_STARTED.value
    assert event_types[1] == SSEEventType.THINKING.value
    
    delta_events = [e for e in events if e["event"] == SSEEventType.TEXT_DELTA.value]
    assert len(delta_events) == 5
    
    assert event_types[-3] == SSEEventType.TEXT_COMPLETED.value
    assert event_types[-2] == SSEEventType.AVATAR_STATE.value
    assert event_types[-1] == SSEEventType.INTERACTION_COMPLETED.value

    # Verify sequence integrity
    for i, event in enumerate(events, start=1):
        assert event["id"] == f"INT-STREAM-001:{i}"
