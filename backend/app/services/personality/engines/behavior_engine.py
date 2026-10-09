import time
from typing import Optional, Dict, Any, List
from app.services.personality.models.personality_state import PersonalityState
from app.services.personality.models.behavior_directive import (
    BehaviorDirective,
    ResponseStyle,
    InteractionBehavior,
    EmotionalExpressionDirective
)
from app.services.personality.engines.trait_engine import TraitEngine
from app.services.personality.engines.communication_engine import CommunicationEngine
from app.services.personality.engines.attachment_engine import AttachmentEngine
from app.domain.relationship.relationship_stage import RelationshipStage

class PersonalityBehaviorEngine:
    """
    Core Behavioral Decision Engine (<10ms).
    Synthesizes PersonalityState, Emotion, Relationship, Memory, and User Input into an actionable BehaviorDirective.
    """

    @staticmethod
    def resolve_behavior(
        personality: Optional[PersonalityState] = None,
        emotion: Optional[Dict[str, Any]] = None,
        relationship_stage: RelationshipStage = RelationshipStage.FRIEND,
        memory_context: Optional[List[str]] = None,
        user_input: str = ""
    ) -> BehaviorDirective:
        t0 = time.perf_counter()
        reasons: List[str] = []
        input_lower = user_input.lower().strip()

        if personality is None:
            personality = PersonalityState()

        # 1. Detect Contextual Triggers
        is_user_distressed = any(kw in input_lower for kw in ["힘들어", "지쳤어", "속상해", "우울해", "피곤해", "tired", "sad", "exhausted", "struggling"])
        is_user_celebrating = any(kw in input_lower for kw in ["성공", "해냈어", "합격", "완성", "won", "passed", "succeeded", "celebrate"])
        is_serious = is_user_distressed or any(kw in input_lower for kw in ["고민", "결정", "비밀", "상담", "advice", "serious"])

        if is_user_distressed:
            reasons.append("user_negative_emotion_detected")
        if is_user_celebrating:
            reasons.append("user_milestone_celebration")
        reasons.append(f"relationship_{relationship_stage.value}")

        # 2. Modulate Sub-Engines
        fatigue = 0.0
        if emotion and "energy" in emotion:
            fatigue = max(0.0, 1.0 - emotion["energy"])

        mod_traits = TraitEngine.modulate_traits(
            base_traits=personality.core_traits,
            is_user_distressed=is_user_distressed,
            is_user_celebrating=is_user_celebrating,
            companion_fatigue=fatigue
        )

        mod_comm = CommunicationEngine.resolve_communication(
            base_style=personality.communication_style,
            stage=relationship_stage,
            is_serious_topic=is_serious
        )

        mod_attach = AttachmentEngine.resolve_attachment(
            base_attachment=personality.attachment_style,
            stage=relationship_stage
        )

        # 3. Formulate Response Style
        resp_style = ResponseStyle(
            warmth=mod_traits.warmth,
            humor=mod_comm.humor,
            directness=mod_comm.directness,
            playfulness=mod_traits.playfulness
        )

        # 4. Formulate Interaction Behavior
        # Teasing only allowed when relationship >= FRIEND, playfulness >= 0.5, and NOT distressed
        can_tease = (
            relationship_stage in [RelationshipStage.FRIEND, RelationshipStage.CLOSE_FRIEND, RelationshipStage.TRUSTED_COMPANION]
            and mod_traits.playfulness >= 0.5
            and not is_user_distressed
            and not is_serious
        )

        interact_behavior = InteractionBehavior(
            ask_followup=(mod_traits.curiosity >= 0.5),
            tease_user=can_tease,
            show_concern=is_user_distressed or (mod_traits.empathy >= 0.7),
            initiate_topic=(mod_attach.initiative >= 0.6)
        )

        # 5. Formulate Emotional Expression Directive for Avatar
        expression = "gentle_smile"
        intensity = 0.65
        if is_user_distressed:
            expression = "empathetic_listening"
            intensity = 0.85
        elif is_user_celebrating:
            expression = "happy_smile"
            intensity = 0.95
        elif can_tease:
            expression = "playful_wink"
            intensity = 0.75

        expr_directive = EmotionalExpressionDirective(
            expression=expression,
            intensity=intensity
        )

        # Check performance
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        reasons.append(f"engine_latency_{elapsed_ms:.2f}ms")

        return BehaviorDirective(
            response_style=resp_style,
            interaction_behavior=interact_behavior,
            emotional_expression=expr_directive,
            reasons=reasons
        )
