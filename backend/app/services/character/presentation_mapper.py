from app.services.character.domain import CharacterDecision, BehaviorIntent, ResponseStyleType, PresentationIntent

class PresentationIntentMapper:
    """
    Translates high-level CharacterDecision into structured PresentationIntent for Avatar rendering.
    """

    @staticmethod
    def map_decision_to_presentation(decision: CharacterDecision) -> PresentationIntent:
        expression = "neutral"
        gesture = "idle"
        intensity = decision.emotional_intensity
        gaze = "direct"
        energy = decision.initiative_level

        # Map by Behavior Intents
        if BehaviorIntent.COMFORT_USER in decision.behavior_intents or decision.response_style == ResponseStyleType.GENTLE_LISTENING:
            expression = "gentle_listening"
            gesture = "hand_on_chest"
            gaze = "soft"
            energy = max(0.3, decision.emotional_intensity * 0.6)
        elif BehaviorIntent.CELEBRATE_SUCCESS in decision.behavior_intents or decision.response_style == ResponseStyleType.CHEERFUL_ENERGETIC:
            expression = "happy_smile"
            gesture = "celebration_wave"
            gaze = "enthusiastic"
            energy = 0.9
            intensity = 0.95
        elif BehaviorIntent.TEASE_PLAYFULLY in decision.behavior_intents or decision.response_style == ResponseStyleType.PLAYFUL_TEASING:
            expression = "playful_wink"
            gesture = "head_tilt"
            gaze = "direct"
            energy = 0.75
        elif decision.response_style == ResponseStyleType.CALM_REFLECTIVE:
            expression = "thoughtful"
            gesture = "chin_touch"
            gaze = "contemplative"
            energy = 0.4
        else:
            expression = "gentle_smile"
            gesture = "attentive_nod"
            energy = 0.6

        return PresentationIntent(
            facial_expression=expression,
            gesture_type=gesture,
            gesture_intensity=round(intensity, 2),
            gaze_behavior=gaze,
            animation_energy=round(energy, 2)
        )
