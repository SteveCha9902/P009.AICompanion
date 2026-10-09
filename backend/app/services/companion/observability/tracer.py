import time
import json
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger("companion.observability")

class InteractionTracer:
    """
    Measures and emits structured JSON observability logs for Companion Interactions.
    Keeps Developer Observability decoupled from User-facing SSE protocol.
    Includes comprehensive token usage and latency metrics.
    """
    def __init__(self, interaction_id: str, user_id: str, companion_id: str, modality: str = "text", model: Optional[str] = None):
        self.interaction_id = interaction_id
        self.user_id = user_id
        self.companion_id = companion_id
        self.modality = modality
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        self.start_time = time.time()
        self.input_norm_start: Optional[float] = None
        self.input_norm_end: Optional[float] = None
        self.context_start: Optional[float] = None
        self.context_end: Optional[float] = None
        self.llm_start: Optional[float] = None
        self.first_token_time: Optional[float] = None
        self.llm_end: Optional[float] = None
        self.post_process_start: Optional[float] = None
        self.post_process_end: Optional[float] = None
        self.end_time: Optional[float] = None
        self.error: Optional[str] = None
        
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.total_tokens: int = 0

    def mark_input_norm_start(self):
        self.input_norm_start = time.time()

    def mark_input_norm_end(self):
        self.input_norm_end = time.time()

    def mark_context_start(self):
        self.context_start = time.time()

    def mark_context_end(self):
        self.context_end = time.time()

    def mark_llm_start(self):
        self.llm_start = time.time()

    def mark_first_token(self):
        if self.first_token_time is None:
            self.first_token_time = time.time()
        self.output_tokens += 1
        self.total_tokens = self.input_tokens + self.output_tokens

    def mark_token(self):
        self.output_tokens += 1
        self.total_tokens = self.input_tokens + self.output_tokens

    def set_token_usage(self, input_tokens: int, output_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens

    def mark_llm_end(self):
        self.llm_end = time.time()

    def mark_post_process_start(self):
        self.post_process_start = time.time()

    def mark_post_process_end(self):
        self.post_process_end = time.time()

    def mark_error(self, err: str):
        self.error = str(err)
        self.end_time = time.time()
        self.emit_log()

    def mark_completed(self):
        self.end_time = time.time()
        self.emit_log()

    def get_metrics(self) -> Dict[str, Any]:
        def diff_ms(t_start, t_end) -> Optional[int]:
            if t_start and t_end:
                return int((t_end - t_start) * 1000)
            return None

        input_norm_ms = diff_ms(self.input_norm_start, self.input_norm_end)
        context_gather_ms = diff_ms(self.context_start, self.context_end)
        ttft_ms = diff_ms(self.llm_start, self.first_token_time)
        llm_total_ms = diff_ms(self.llm_start, self.llm_end)
        post_process_ms = diff_ms(self.post_process_start, self.post_process_end)
        total_e2e_ms = diff_ms(self.start_time, self.end_time or time.time())

        return {
            "interaction_id": self.interaction_id,
            "user_id": self.user_id,
            "companion_id": self.companion_id,
            "modality": self.modality,
            "model": self.model,
            "token_count": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "input_norm_ms": input_norm_ms,
            "context_gather_ms": context_gather_ms,
            "ttft_ms": ttft_ms,
            "llm_total_ms": llm_total_ms,
            "post_process_ms": post_process_ms,
            "total_e2e_ms": total_e2e_ms,
            "error": self.error,
        }

    def emit_log(self):
        metrics = self.get_metrics()
        logger.info(f"[TRACE] {json.dumps(metrics)}")
