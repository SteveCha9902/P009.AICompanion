from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class CompanionInteractionState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    ANALYZING = "ANALYZING"
    THINKING = "THINKING"
    RESPONDING = "RESPONDING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    PAUSED = "PAUSED"
    ERROR = "ERROR"

class InteractionStateMachine:
    def __init__(self, companion_id: str):
        self.companion_id = companion_id
        self._current_state = CompanionInteractionState.IDLE
        self.last_transition_time = datetime.now(timezone.utc)
        self.current_interaction_id: Optional[str] = None

    @property
    def current_state(self) -> CompanionInteractionState:
        return self._current_state

    def transition_to(self, new_state: CompanionInteractionState, interaction_id: Optional[str] = None):
        """
        Transitions the Companion to a new interaction state.
        Enforces some basic rules (e.g., cannot transition from ERROR easily without reset).
        """
        old_state = self._current_state
        
        # Valid Transitions Rules
        # If INTERRUPTED, we usually go back to LISTENING or IDLE.
        if old_state == CompanionInteractionState.INTERRUPTED and new_state not in (CompanionInteractionState.LISTENING, CompanionInteractionState.IDLE):
            logger.warning(f"Invalid transition from INTERRUPTED to {new_state}. Ignoring unless forced.")
            # We might still allow it in a more robust system, but log it.
            
        self._current_state = new_state
        self.last_transition_time = datetime.now(timezone.utc)
        if interaction_id:
            self.current_interaction_id = interaction_id
            
        logger.info(f"[StateMachine] {self.companion_id} | {old_state.value} -> {new_state.value} ({interaction_id or 'No ID'})")
        
    def interrupt(self):
        """Helper to safely interrupt the current state."""
        self.transition_to(CompanionInteractionState.INTERRUPTED, self.current_interaction_id)
        
    def reset(self):
        """Helper to clear state."""
        self.transition_to(CompanionInteractionState.IDLE, None)
