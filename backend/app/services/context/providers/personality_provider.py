from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.personality.personality_vector import CharacterDNA
from app.services.personality.personality_filter import PersonalityFilter
from app.services.cognitive.cognitive_decision_engine import CognitiveDecisionEngine
from app.services.adaptive.affective_estimator import AffectiveStateEstimator
from app.services.adaptive.adaptive_behavior_planner import AdaptiveBehaviorPlanner
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator

class PersonalityContextProvider(ContextProvider):
    """
    Personality Alignment Provider for ContextBuilder:
    Injects persistent CharacterDNA and Tone & Manner Charter into LLM prompt.
    """

    def __init__(self, companion_id: str = "default_companion"):
        self.companion_id = companion_id
        cid_lower = (companion_id or "").lower()
        if "mani" in cid_lower or "마니" in companion_id:
            self.dna = CharacterDNA(
                warmth=0.98,
                humor=0.85,
                curiosity=0.95,
                empathy=0.92,
                playfulness=0.98,
                formality=0.10,
                optimism=0.95,
                companion_id=companion_id
            )
        elif "hana" in cid_lower or "하나" in companion_id:
            self.dna = CharacterDNA(
                warmth=0.85,
                humor=0.80,
                curiosity=0.90,
                empathy=0.85,
                playfulness=0.85,
                formality=0.20,
                optimism=0.90,
                companion_id=companion_id
            )
        else:
            self.dna = CharacterDNA.default_companion_dna()

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        raw_affective = AffectiveStateEstimator.estimate_affective_state(current_user_message, awareness_ctx)
        planned_affective = AdaptiveBehaviorPlanner.plan_behavior(raw_affective)

        decision = CognitiveDecisionEngine.evaluate_decision("default_user", current_user_message)
        manifest = PersonalityFilter.apply_personality_filter(decision, self.dna, planned_affective)
        guidance = PersonalityFilter.build_personality_prompt_guidance(manifest)

        return [{"role": "system", "content": guidance}]
