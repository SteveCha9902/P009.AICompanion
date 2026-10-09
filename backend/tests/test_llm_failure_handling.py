import pytest
import json
from unittest.mock import AsyncMock
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine
from app.services.companion.domain import NormalizedInput, InputType, SSEEventType
from app.services.llm.base import BaseLLMProvider, LLMAuthError, LLMTimeoutError, LLMRateLimitError

class FailingLLM(BaseLLMProvider):
    def __init__(self, exception_to_raise):
        self.exc = exception_to_raise

    async def generate(self, messages):
        raise self.exc

    async def stream(self, messages):
        raise self.exc
        yield

@pytest.mark.asyncio
async def test_failure_handling_auth_error():
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="comp_f")
    
    mock_context_builder = AsyncMock()
    mock_context_builder.build.return_value = [{"role": "user", "content": "hi"}]

    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_context_builder,
        llm_provider=FailingLLM(LLMAuthError("Invalid API Key")),
        avatar_resolver=None,
        message_repo=None
    )

    user_input = NormalizedInput(
        interaction_id="INT-FAIL-001",
        user_id="user_f",
        companion_id="comp_f",
        conversation_id="conv_f",
        input_type=InputType.TEXT,
        content="hi"
    )

    events = []
    async for chunk in orchestrator.process_interaction(user_input):
        for line in chunk.strip().split("\n"):
            if line.startswith("event:"):
                events.append(line.split(":", 1)[1].strip())

    # Should safely emit error event without throwing uncaught exception
    assert SSEEventType.ERROR.value in events

@pytest.mark.asyncio
async def test_failure_handling_timeout():
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="comp_f")
    
    mock_context_builder = AsyncMock()
    mock_context_builder.build.return_value = [{"role": "user", "content": "hi"}]

    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_context_builder,
        llm_provider=FailingLLM(LLMTimeoutError("Request Timeout")),
        avatar_resolver=None,
        message_repo=None
    )

    user_input = NormalizedInput(
        interaction_id="INT-FAIL-002",
        user_id="user_f",
        companion_id="comp_f",
        conversation_id="conv_f",
        input_type=InputType.TEXT,
        content="hi"
    )

    events = []
    async for chunk in orchestrator.process_interaction(user_input):
        for line in chunk.strip().split("\n"):
            if line.startswith("event:"):
                events.append(line.split(":", 1)[1].strip())

    assert SSEEventType.ERROR.value in events
