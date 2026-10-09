from datetime import datetime, timezone, timedelta
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.repositories.presence_repository import PresenceRepository
import logging

logger = logging.getLogger(__name__)

class PresenceService:
    def __init__(self, repo: PresenceRepository):
        self.repo = repo
        # Define IDLE threshold (e.g., 5 minutes of inactivity)
        self.idle_threshold_minutes = 5
        # Define AWAY threshold (e.g., 60 minutes of inactivity)
        self.away_threshold_minutes = 60

    async def get_state(self, companion_id: str) -> PresenceState:
        state = await self.repo.get_state(companion_id)
        if not state:
            state = PresenceState(companion_id=companion_id, state=PresenceStateEnum.OFFLINE)
            state = await self.repo.save_state(state)
        
        # Automatically transition state based on time if currently AVAILABLE or ENGAGED
        now = datetime.now(timezone.utc)
        if state.state in (PresenceStateEnum.AVAILABLE, PresenceStateEnum.ENGAGED, PresenceStateEnum.IDLE):
            if state.last_active_at:
                minutes_since_active = (now - state.last_active_at).total_seconds() / 60
                
                new_state = state.state
                if minutes_since_active > self.away_threshold_minutes:
                    new_state = PresenceStateEnum.AWAY
                elif minutes_since_active > self.idle_threshold_minutes:
                    new_state = PresenceStateEnum.IDLE
                    
                if new_state != state.state:
                    state.state = new_state
                    state = await self.repo.save_state(state)
                    
        return state

    async def update_heartbeat(self, companion_id: str, is_foreground: bool) -> PresenceState:
        """
        Called by the mobile app's heartbeat or lifecycle observer.
        """
        state = await self.repo.get_state(companion_id)
        if not state:
            state = PresenceState(companion_id=companion_id)
            
        now = datetime.now(timezone.utc)
        state.last_active_at = now
        
        if is_foreground:
            # If they just foregrounded and weren't engaged, they are available.
            if state.state not in (PresenceStateEnum.ENGAGED, PresenceStateEnum.AVAILABLE):
                state.state = PresenceStateEnum.AVAILABLE
        else:
            # If they backgrounded, they aren't engaged anymore, but they might still be available (waiting for push).
            if state.state == PresenceStateEnum.ENGAGED:
                state.state = PresenceStateEnum.AVAILABLE
                
        return await self.repo.save_state(state)
        
    async def mark_interaction(self, companion_id: str) -> PresenceState:
        """
        Called when a user sends a message.
        """
        state = await self.repo.get_state(companion_id)
        if not state:
            state = PresenceState(companion_id=companion_id)
            
        now = datetime.now(timezone.utc)
        state.last_interaction_at = now
        state.last_active_at = now
        state.state = PresenceStateEnum.ENGAGED
        
        return await self.repo.save_state(state)
