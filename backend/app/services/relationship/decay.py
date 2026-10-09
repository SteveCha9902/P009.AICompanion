from datetime import datetime, timezone
from app.db.models.relationship import RelationshipState

class DecayEngine:
    """
    Applies dimension-specific decay to the relationship state.
    """
    
    def apply_decay(self, current_state: RelationshipState, current_time: datetime = None) -> RelationshipState:
        """
        Modifies state in-place or returns a new instance.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        last_time = current_state.updated_at
        if not last_time:
            return current_state

        if last_time.tzinfo is None and current_time.tzinfo is not None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        elif last_time.tzinfo is not None and current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
            
        days_passed = (current_time - last_time).total_seconds() / (60 * 60 * 24)
        
        if days_passed < 1:
            return current_state
            
        # Very slow decay for Trust & Reliability (e.g., -0.01 per 30 days)
        trust_decay = (days_passed / 30.0) * 0.01
        current_state.trust = max(0.1, current_state.trust - trust_decay)
        current_state.reliability = max(0.1, current_state.reliability - trust_decay)
        
        # Slow decay for Familiarity (e.g., -0.01 per 15 days)
        familiarity_decay = (days_passed / 15.0) * 0.01
        current_state.familiarity = max(0.1, current_state.familiarity - familiarity_decay)
        
        # Medium decay for Closeness (e.g., -0.02 per 10 days)
        closeness_decay = (days_passed / 10.0) * 0.02
        current_state.closeness = max(0.1, current_state.closeness - closeness_decay)
        
        # Fast decay for Engagement (e.g., -0.05 per 3 days)
        engagement_decay = (days_passed / 3.0) * 0.05
        current_state.engagement = max(0.1, current_state.engagement - engagement_decay)
        
        return current_state
