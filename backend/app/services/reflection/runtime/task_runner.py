import asyncio
import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

class ReflectionTaskRunner:
    """
    Asynchronous Task Runner ensuring complete latency isolation from user response pipeline.
    """

    @staticmethod
    def run_async(coro_fn: Callable[[], Awaitable[None]], task_name: str = "reflection_task"):
        async def _safe_run():
            try:
                await coro_fn()
            except Exception as e:
                logger.error(f"[ReflectionTaskRunner] Error in background task '{task_name}': {e}", exc_info=True)

        asyncio.create_task(_safe_run())
