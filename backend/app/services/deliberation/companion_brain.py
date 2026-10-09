from typing import Dict, Any, Optional
from app.domain.deliberation.deliberation_types import FinalCompanionDecision
from app.services.deliberation.deliberation_engine import DeliberationEngine

class CompanionBrain:
    """
    Unified Companion Brain (Companion OS v1.0).
    Orchestrates the entire L1~L12 Cognitive Architecture:
    L1 Memory -> L2 Relationship -> L3 Tone -> L4 Goals -> L5 Identity ->
    L6 Autonomy -> L7 Safety -> L8 Constitution -> L9 Observability ->
    L10 Self-Improvement -> L11 World Model -> L12 Unified Deliberation Brain.
    """

    @classmethod
    def think_and_decide(
        cls,
        user_id: str,
        text_input: str,
        context_data: Optional[Dict[str, Any]] = None,
        topic: str = ""
    ) -> FinalCompanionDecision:
        return DeliberationEngine.deliberate(
            user_id=user_id,
            text_input=text_input,
            context_data=context_data,
            topic=topic
        )
