from typing import List, Optional
from app.services.character.growth.domain import CharacterGlobalGrowthState, UserRelationshipAdaptationState

class CharacterGrowthEngine:
    """
    Evolves Global Growth Habits and User-Specific Adaptations without contaminating Immutable Core.
    """

    @staticmethod
    def adapt_user_style(
        current_adaptation: UserRelationshipAdaptationState,
        signal: str
    ) -> UserRelationshipAdaptationState:
        formality = current_adaptation.preferred_formality
        humor = current_adaptation.preferred_humor
        directness = current_adaptation.preferred_directness
        supp_pref = current_adaptation.support_preference

        # Modulate preferences based on repeated user cues
        if signal == "user_prefers_formal":
            formality = min(0.9, formality + 0.05)
        elif signal == "user_prefers_casual":
            formality = max(0.1, formality - 0.05)
            humor = min(0.85, humor + 0.05)
        elif signal == "user_needs_direct_advice":
            directness = min(0.9, directness + 0.05)
            supp_pref = "PRACTICAL_ADVICE"
        elif signal == "user_needs_listening":
            supp_pref = "EMPATHIC_SUPPORT"

        return UserRelationshipAdaptationState(
            user_id=current_adaptation.user_id,
            companion_id=current_adaptation.companion_id,
            preferred_formality=round(formality, 2),
            preferred_humor=round(humor, 2),
            preferred_directness=round(directness, 2),
            support_preference=supp_pref,
            conversation_rhythm=current_adaptation.conversation_rhythm
        )

    @staticmethod
    def evolve_global_growth(
        current_growth: CharacterGlobalGrowthState,
        reflection_insights: List[str]
    ) -> CharacterGlobalGrowthState:
        habits = list(current_growth.global_learned_behavior)

        for ins in reflection_insights:
            if ins not in habits:
                habits.append(ins)

        # Keep top learned habits
        return CharacterGlobalGrowthState(
            companion_id=current_growth.companion_id,
            support_style=current_growth.support_style,
            initiative_tendency=current_growth.initiative_tendency,
            global_learned_behavior=habits[-10:]
        )
