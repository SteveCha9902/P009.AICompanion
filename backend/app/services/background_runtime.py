import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from app.db.models.companion import Companion
from app.db.models.presence import PresenceState
from app.services.proactive_service import ProactiveService
from app.services.notification.provider_interface import BaseNotificationProvider

logger = logging.getLogger(__name__)

class BackgroundRuntime:
    def __init__(self, db_session_maker, proactive_service: ProactiveService, notification_provider: BaseNotificationProvider):
        self.db_session_maker = db_session_maker
        self.proactive_service = proactive_service
        self.notification_provider = notification_provider
        self.running = False
        self._task = None

    async def start(self, interval_seconds: int = 300):
        """Start the background evaluation loop (e.g. every 5 minutes)."""
        if self.running:
            return
            
        self.running = True
        self._task = asyncio.create_task(self._loop(interval_seconds))
        logger.info(f"BackgroundRuntime started with interval {interval_seconds}s")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("BackgroundRuntime stopped")

    async def _loop(self, interval_seconds: int):
        while self.running:
            try:
                await self._evaluate_companions()
            except Exception as e:
                logger.error(f"Error in BackgroundRuntime loop: {e}")
                
            await asyncio.sleep(interval_seconds)

    async def _evaluate_companions(self):
        """
        Evaluate all companions for potential background interactions (Proactive).
        In a real scenario, this would distribute tasks or run in a Celery beat worker.
        """
        with self.db_session_maker() as db:
            # For simplicity, get all companions. Ideally, filter by ones that have Background mode ON.
            companions = db.query(Companion).all()
            
            for companion in companions:
                try:
                    # Logic to check if we should send a proactive notification
                    # This involves the ProactiveEngine
                    
                    # 1. Check if companion is in BACKGROUND Device State (assume handled here)
                    # 2. Check Presence (we need it to be AVAILABLE or similar)
                    presence = db.query(PresenceState).filter(PresenceState.companion_id == companion.id).first()
                    if not presence or presence.state == "OFFLINE":
                        continue
                        
                    # Here we would invoke proactive_service to evaluate TIME_BASED triggers
                    # If allowed, generate message -> create PendingInteraction -> send Push
                    # (Implementation simplified for demonstration)
                    pass
                except Exception as e:
                    logger.error(f"Error evaluating companion {companion.id}: {e}")
