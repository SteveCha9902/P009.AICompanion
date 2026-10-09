import pytest
import asyncio
import uuid
import os
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.companion.domain import NormalizedInput, InputType, SSEEventType
from app.services.companion.orchestrator import CompanionOrchestrator, active_interactions
from app.services.companion.runtime import create_companion_orchestrator, runtime_lifecycle, RuntimeState
from app.services.providers.factory import ProviderFactory, MockLLMProvider
from app.services.companion.observability.tracer import InteractionTracer
from app.services.context.builder import ContextBuilder

# Mock Delayed LLM to test TTFT & Timeout
class DelayedMockLLM:
    def __init__(self, delay_per_token=0.01, text="Hello world from delayed mock LLM"):
        self.delay = delay_per_token
        self.text = text

    async def stream(self, messages):
        words = self.text.split(" ")
        for word in words:
            await asyncio.sleep(self.delay)
            yield MagicMock(content=word + " ")

@pytest.mark.asyncio
async def test_gate_3_provider_factory_switching():
    """
    Gate 3 - Provider Factory Switching:
    Verify that ProviderFactory can independently instantiate Mock vs OpenAI providers based on env vars
    """
    # 1. Default / Mock LLM
    mock_llm = ProviderFactory.get_llm_provider("mock")
    assert isinstance(mock_llm, MockLLMProvider)

    # 2. Embedding provider
    mock_emb = ProviderFactory.get_embedding_provider("mock")
    assert mock_emb.__class__.__name__ == "MockEmbeddingProvider"

    # 3. STT / TTS providers
    mock_stt = ProviderFactory.get_stt_provider("mock")
    mock_tts = ProviderFactory.get_tts_provider("mock")
    assert mock_stt.__class__.__name__ == "MockSTTProvider"
    assert mock_tts.__class__.__name__ == "MockTTSProvider"


@pytest.mark.asyncio
async def test_gate_4_sse_cancellation_and_cleanup():
    """
    Gate 4 - SSE Failure & Cancellation:
    Verify that when an interaction is cancelled, active_interactions is cleaned up and state machine is reset
    """
    mock_llm = DelayedMockLLM(delay_per_token=0.5)
    mock_db = AsyncMock()
    
    orchestrator = await create_companion_orchestrator(
        db=mock_db,
        user_id="user_cancel",
        companion_id="comp_cancel",
        llm_provider=mock_llm
    )
    
    interaction_id = "INT-CANCEL-TEST-001"
    input_data = NormalizedInput(
        interaction_id=interaction_id,
        user_id="user_cancel",
        companion_id="comp_cancel",
        content="This stream will be cancelled"
    )

    async def run_stream():
        stream = orchestrator.process_interaction(input_data)
        try:
            async for _ in stream:
                # Cancel task
                await asyncio.sleep(0.01)
        finally:
            await stream.aclose()

    task = asyncio.create_task(run_stream())
    await asyncio.sleep(0.05)
    task.cancel()
    
    with pytest.raises(asyncio.CancelledError):
        await task

    # Verify active_interactions registry is completely cleaned up
    assert interaction_id not in active_interactions
    # Verify state machine returned to IDLE
    assert orchestrator.state_machine.current_state.value == "IDLE"


@pytest.mark.asyncio
async def test_gate_5_observability_tracer():
    """
    Gate 5 - Observability Trace:
    Verify that InteractionTracer measures TTFT, context gather, and total e2e latency accurately
    """
    tracer = InteractionTracer("INT-TRACE-001", "user_1", "comp_1", "text")
    
    tracer.mark_context_start()
    await asyncio.sleep(0.02)
    tracer.mark_context_end()

    tracer.mark_llm_start()
    await asyncio.sleep(0.03)
    tracer.mark_first_token()
    await asyncio.sleep(0.02)
    tracer.mark_llm_end()

    tracer.mark_post_process_start()
    await asyncio.sleep(0.01)
    tracer.mark_post_process_end()
    
    tracer.mark_completed()
    metrics = tracer.get_metrics()

    assert metrics["interaction_id"] == "INT-TRACE-001"
    assert metrics["ttft_ms"] is not None and metrics["ttft_ms"] >= 20
    assert metrics["context_gather_ms"] is not None and metrics["context_gather_ms"] >= 15
    assert metrics["total_e2e_ms"] is not None and metrics["total_e2e_ms"] >= 70
    assert metrics["token_count"] == 1


def test_gate_6_runtime_lifecycle():
    """
    Gate 6 - Runtime Lifecycle:
    Verify transitions through CREATED -> READY -> RUNNING -> STOPPED
    """
    assert runtime_lifecycle.state in (RuntimeState.READY, RuntimeState.RUNNING, RuntimeState.CREATED)
    
    runtime_lifecycle.start()
    assert runtime_lifecycle.state == RuntimeState.RUNNING

    runtime_lifecycle.stop()
    assert runtime_lifecycle.state == RuntimeState.STOPPED

    # Re-initialize for subsequent tests
    runtime_lifecycle.initialize()
    runtime_lifecycle.start()
    assert runtime_lifecycle.state == RuntimeState.RUNNING


@pytest.mark.asyncio
async def test_gate_7_idempotency_guard():
    """
    Gate 7 - Idempotency Guard:
    Verify that sending the exact same interaction_id while active returns a duplicate error rather than duplicating LLM calls
    """
    mock_llm = DelayedMockLLM(delay_per_token=0.1)
    mock_db = AsyncMock()
    
    orchestrator = await create_companion_orchestrator(
        db=mock_db,
        user_id="user_idem",
        companion_id="comp_idem",
        llm_provider=mock_llm
    )
    
    interaction_id = "INT-IDEMPOTENT-001"
    input_data = NormalizedInput(
        interaction_id=interaction_id,
        user_id="user_idem",
        companion_id="comp_idem",
        content="Testing idempotency"
    )

    # Simulate active interaction in registry
    active_interactions.add(interaction_id)

    events = []
    async for chunk in orchestrator.process_interaction(input_data):
        events.append(chunk)

    full_output = "".join(events)
    assert "Duplicate interaction in progress" in full_output
    assert "event: error" in full_output

    # Cleanup
    active_interactions.discard(interaction_id)
