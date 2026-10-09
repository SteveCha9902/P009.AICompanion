import asyncio
import logging
from typing import Callable, Dict, List, Awaitable
from collections import defaultdict
from app.services.companion.events.events import CompanionEvent, EventPriority, EventType

logger = logging.getLogger(__name__)

EventHandler = Callable[[CompanionEvent], Awaitable[None]]

class CompanionEventBus:
    """
    Event Bus for Orchestrator -> Engine decoupling.
    Supports Sync (blocking execution for critical path) and Async (fire and forget) handlers.
    """
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
    
    def subscribe(self, event_type: EventType, handler: EventHandler):
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler {handler.__name__} to {event_type}")

    async def publish(self, event: CompanionEvent):
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return

        if event.priority == EventPriority.SYNC:
            # Execute critical path synchronously (but concurrently via gather)
            logger.info(f"[EventBus] SYNC Executing {event.event_type} ({event.interaction_id})")
            await asyncio.gather(*(handler(event) for handler in handlers))
        else:
            # Fire and forget for background tasks
            logger.info(f"[EventBus] ASYNC Dispatching {event.event_type} ({event.interaction_id})")
            for handler in handlers:
                asyncio.create_task(self._safe_execute_async(handler, event))

    async def _safe_execute_async(self, handler: EventHandler, event: CompanionEvent):
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"[EventBus] Error in ASYNC handler {handler.__name__} for {event.event_type}: {e}")
            # Failure Isolation: Async failures never crash the main pipeline
