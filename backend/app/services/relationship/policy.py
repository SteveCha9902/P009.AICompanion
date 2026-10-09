from app.db.models.relationship import RelationshipState, RelationshipSignalType, SignalSeverity, RelationshipLevel
from typing import Tuple

class PolicyEngine:
    """
    Evaluates Interaction Signals and outputs delta for relationship dimensions.
    """
    
    def __init__(self):
        # Maximum delta per interaction to prevent rapid swings
        self.MAX_DELTA = 0.05
        
        # Base modifiers based on severity (0.0 to 1.0 multiplier)
        self.severity_multiplier = {
            SignalSeverity.LOW: 0.2,
            SignalSeverity.MEDIUM: 0.5,
            SignalSeverity.HIGH: 1.0,
            SignalSeverity.CRITICAL: 2.0  # Allowed to exceed MAX_DELTA slightly for critical events
        }

    def evaluate_signal(self, signal_type: RelationshipSignalType, severity: SignalSeverity) -> dict:
        """
        Returns a dictionary of dimension deltas based on signal and severity.
        """
        multiplier = self.severity_multiplier.get(severity, 0.5)
        
        # Base deltas (will be multiplied by severity)
        deltas = {}
        
        if signal_type == RelationshipSignalType.COMPANION_HELPED_SUCCESSFULLY:
            deltas['trust'] = 0.03
            deltas['reliability'] = 0.04
            
        elif signal_type == RelationshipSignalType.COMPANION_FAILED:
            deltas['trust'] = -0.04
            deltas['reliability'] = -0.05
            
        elif signal_type == RelationshipSignalType.USER_ADAPTATION_SUCCESS:
            deltas['trust'] = 0.02
            deltas['familiarity'] = 0.03
            deltas['reliability'] = 0.03
            
        elif signal_type == RelationshipSignalType.USER_SHARED_PERSONAL_INFO:
            deltas['closeness'] = 0.04
            deltas['familiarity'] = 0.05
            
        elif signal_type == RelationshipSignalType.COMPANION_REMEMBERED:
            deltas['trust'] = 0.04
            deltas['familiarity'] = 0.03
            
        elif signal_type == RelationshipSignalType.COMPANION_FORGOT:
            deltas['reliability'] = -0.04
            deltas['closeness'] = -0.02
            
        elif signal_type == RelationshipSignalType.USER_RETURNED:
            deltas['engagement'] = 0.10 # Engagement is volatile
            
        elif signal_type == RelationshipSignalType.USER_EXPRESSED_TRUST:
            deltas['trust'] = 0.05
            
        # Apply multiplier and cap
        final_deltas = {}
        for dim, value in deltas.items():
            delta = value * multiplier
            # Apply max cap (unless critical drop)
            if delta > 0:
                delta = min(delta, self.MAX_DELTA)
            else:
                delta = max(delta, -self.MAX_DELTA * (2 if severity == SignalSeverity.CRITICAL else 1))
            final_deltas[dim] = delta
            
        return final_deltas

    def calculate_level(self, state: RelationshipState) -> RelationshipLevel:
        """
        Calculate semantic level based mainly on Trust, Familiarity, and Closeness.
        """
        # Weighted average or specific thresholds
        score = (state.trust * 0.4) + (state.familiarity * 0.3) + (state.closeness * 0.3)
        
        if score < 0.2:
            return RelationshipLevel.STRANGER
        elif score < 0.4:
            return RelationshipLevel.ACQUAINTANCE
        elif score < 0.6:
            return RelationshipLevel.FAMILIAR
        elif score < 0.8:
            return RelationshipLevel.CLOSE
        else:
            return RelationshipLevel.TRUSTED

class BehaviorPolicy:
    """
    Translates Relationship State into Behavior Modifiers for the LLM Context.
    """
    def get_behavior_modifiers(self, state: RelationshipState, level: RelationshipLevel) -> list[str]:
        modifiers = []
        
        if level == RelationshipLevel.STRANGER:
            modifiers.append("Be polite, helpful, and clear. Avoid assuming preferences.")
            modifiers.append("Explain things comprehensively.")
            
        elif level == RelationshipLevel.ACQUAINTANCE:
            modifiers.append("Be friendly and polite. You are starting to learn about the user.")
            
        elif level == RelationshipLevel.FAMILIAR:
            modifiers.append("You are familiar with the user. Reduce repetitive explanations.")
            modifiers.append("Reference relevant shared history if appropriate.")
            
        elif level == RelationshipLevel.CLOSE:
            modifiers.append("Use a natural, close conversational expression.")
            modifiers.append("You understand the user well. Skip unnecessary formalities.")
            
        elif level == RelationshipLevel.TRUSTED:
            modifiers.append("You have a highly trusted bond. Allow for direct, honest feedback.")
            modifiers.append("Use natural, close expression and implicitly understand their context.")

        if state.engagement < 0.3:
            modifiers.append("The user has been less engaged recently; gently welcome them back without being overbearing.")
            
        return modifiers
