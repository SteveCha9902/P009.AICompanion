import pytest
import time
from app.services.companion.observability.tracer import InteractionTracer

def test_interaction_tracer_metrics_completeness():
    tracer = InteractionTracer(
        interaction_id="INT-TRACE-001",
        user_id="user_trace",
        companion_id="comp_trace",
        modality="text",
        model="gpt-4o-mini"
    )

    # Simulate steps
    tracer.mark_input_norm_start()
    time.sleep(0.01)
    tracer.mark_input_norm_end()

    tracer.mark_context_start()
    time.sleep(0.01)
    tracer.mark_context_end()

    tracer.mark_llm_start()
    time.sleep(0.01)
    tracer.mark_first_token()
    tracer.mark_token()
    tracer.mark_token()
    time.sleep(0.01)
    tracer.mark_llm_end()

    tracer.mark_post_process_start()
    time.sleep(0.01)
    tracer.mark_post_process_end()

    tracer.set_token_usage(input_tokens=150, output_tokens=30)
    tracer.mark_completed()

    metrics = tracer.get_metrics()

    assert metrics["interaction_id"] == "INT-TRACE-001"
    assert metrics["user_id"] == "user_trace"
    assert metrics["companion_id"] == "comp_trace"
    assert metrics["modality"] == "text"
    assert metrics["model"] == "gpt-4o-mini"
    assert metrics["input_tokens"] == 150
    assert metrics["output_tokens"] == 30
    assert metrics["total_tokens"] == 180

    # Verify all timing metrics are measured
    assert metrics["input_norm_ms"] is not None and metrics["input_norm_ms"] >= 0
    assert metrics["context_gather_ms"] is not None and metrics["context_gather_ms"] >= 0
    assert metrics["ttft_ms"] is not None and metrics["ttft_ms"] >= 0
    assert metrics["llm_total_ms"] is not None and metrics["llm_total_ms"] >= 0
    assert metrics["post_process_ms"] is not None and metrics["post_process_ms"] >= 0
    assert metrics["total_e2e_ms"] is not None and metrics["total_e2e_ms"] >= 0
    assert metrics["error"] is None
