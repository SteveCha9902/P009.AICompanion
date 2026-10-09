import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.relationship import RelationshipState, RelationshipEvent, RelationshipSignalType, SignalSeverity
from app.repositories.relationship_repository import RelationshipRepository
from app.services.relationship.policy import PolicyEngine, BehaviorPolicy
from app.services.relationship.decay import DecayEngine

logger = logging.getLogger(__name__)

class RelationshipService:
    def __init__(
        self,
        session: AsyncSession,
        relationship_repo: RelationshipRepository,
        policy_engine: PolicyEngine,
        behavior_policy: BehaviorPolicy,
        decay_engine: DecayEngine
    ):
        self.session = session
        self.repo = relationship_repo
        self.policy_engine = policy_engine
        self.behavior_policy = behavior_policy
        self.decay_engine = decay_engine

    async def get_current_state(self, companion_id: str) -> RelationshipState:
        """
        Retrieves the current state, applying decay if necessary.
        """
        state = await self.repo.get_state(companion_id)
        if not state:
            # Return default state
            state = RelationshipState(companion_id=companion_id)
            state = await self.repo.save_state(state)
            
        # Apply decay based on current time
        decayed_state = self.decay_engine.apply_decay(state)
        
        # Save decayed state
        return await self.repo.save_state(decayed_state)

    async def apply_signal(
        self, 
        companion_id: str, 
        signal_type: RelationshipSignalType, 
        severity: SignalSeverity,
        conversation_id: str = None,
        message_id: str = None,
        reason: str = None
    ):
        """
        Applies a validated relationship signal to update the state and log the event.
        """
        try:
            state = await self.get_current_state(companion_id)
            
            # Calculate Deltas
            deltas = self.policy_engine.evaluate_signal(signal_type, severity)
            if not deltas:
                return state
                
            # Apply Deltas and Bounds
            for dim, delta in deltas.items():
                current_val = getattr(state, dim)
                new_val = max(0.0, min(1.0, current_val + delta))
                setattr(state, dim, new_val)
                
            # Calculate New Level
            state.relationship_level = self.policy_engine.calculate_level(state)
            
            # Save State
            saved_state = await self.repo.save_state(state)
            
            # Log Event
            event = RelationshipEvent(
                companion_id=companion_id,
                conversation_id=conversation_id,
                message_id=message_id,
                signal_type=signal_type,
                severity=severity,
                dimension_changed=", ".join(deltas.keys()),
                delta_applied=", ".join([f"{v:+.3f}" for v in deltas.values()]),
                reason=reason
            )
            await self.repo.log_event(event)
            
            return saved_state

        except Exception as e:
            logger.error(f"Failed to apply relationship signal: {e}")
            return None

    async def get_behavior_modifiers(self, companion_id: str) -> List[str]:
        """
        Returns a list of behavioral modifier strings based on the current relationship.
        """
        state = await self.get_current_state(companion_id)
        return self.behavior_policy.get_behavior_modifiers(state, state.relationship_level)
