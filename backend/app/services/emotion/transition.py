from app.db.models.emotion import EmotionState, EmotionType
from typing import Dict, Any

class TransitionEngine:
    """
    Decides the New Companion State based on Previous State, Emotion Signal, Persona, and Memory.
    This separates the logic from LLM generation.
    """

    def calculate_transition(
        self,
        previous_state: EmotionState,
        emotion_signal: Dict[str, Any],
        persona_base_warmth: float = 0.5
    ) -> EmotionState:
        """
        Returns a newly calculated EmotionState (in memory, unsaved)
        """
        user_emotion = emotion_signal.get("user_emotion", "NEUTRAL")
        intensity = emotion_signal.get("intensity", 0.0)
        
        # Start with previous state's values (assuming decay has already been applied if necessary)
        new_primary = previous_state.primary_emotion
        new_valence = previous_state.valence
        new_arousal = previous_state.arousal
        new_warmth = previous_state.warmth
        new_tension = previous_state.tension
        new_engagement = previous_state.engagement
        
        # Simplified Transition Rules
        if user_emotion == "JOY":
            new_primary = EmotionType.JOY
            new_valence = min(1.0, new_valence + (0.5 * intensity))
            new_arousal = min(1.0, new_arousal + (0.3 * intensity))
            new_warmth = min(1.0, new_warmth + (0.2 * intensity))
            new_tension = max(0.0, new_tension - 0.2)
            new_engagement = min(1.0, new_engagement + 0.2)
            
        elif user_emotion == "SADNESS":
            new_primary = EmotionType.EMPATHY
            new_valence = max(-0.5, new_valence - (0.3 * intensity))
            new_arousal = max(0.0, new_arousal - 0.2)
            # Warmth increases to comfort the user
            new_warmth = min(1.0, new_warmth + (0.4 * intensity))
            new_tension = min(1.0, new_tension + 0.1)
            
        elif user_emotion == "ANGER":
            # If user is angry, be calm and careful (high tension, low arousal, empathy or calm)
            new_primary = EmotionType.CALM
            new_valence = max(-0.5, new_valence - (0.4 * intensity))
            new_arousal = max(0.0, new_arousal - (0.4 * intensity)) # Keep calm
            new_tension = min(1.0, new_tension + (0.5 * intensity))
            new_engagement = min(1.0, new_engagement + 0.3)
            
        elif user_emotion == "AFFECTION":
            new_primary = EmotionType.AFFECTION
            new_valence = min(1.0, new_valence + (0.6 * intensity))
            new_warmth = min(1.0, new_warmth + (0.5 * intensity))
            new_arousal = min(1.0, new_arousal + 0.2)
            new_tension = max(0.0, new_tension - 0.3)
            
        else:
            # For neutral or others, drift slightly towards calm
            pass
            
        # Ensure values stay in bounds
        new_state = EmotionState(
            companion_id=previous_state.companion_id,
            primary_emotion=new_primary,
            valence=max(-1.0, min(1.0, new_valence)),
            arousal=max(0.0, min(1.0, new_arousal)),
            warmth=max(0.0, min(1.0, new_warmth)),
            engagement=max(0.0, min(1.0, new_engagement)),
            tension=max(0.0, min(1.0, new_tension))
        )
        return new_state
