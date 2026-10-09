from typing import List, Optional
from app.domain.world_model.situation_model import (
    SituationModel,
    EnvironmentalFactors,
    SituationHypothesis,
    AnticipatedSupportOpportunity
)
from app.services.world_model.causal_reasoning_engine import CausalReasoningEngine
from app.services.world_model.routine_detector import RoutineDetector
from app.services.world_model.forecast_engine import ForecastEngine

class SituationProvider:
    """
    Synthesizes Hypotheses, Routines, Environmental Factors, and Support Opportunities into a Unified SituationModel.
    Provides context for CCOS decision making.
    """

    @classmethod
    def build_situation_model(
        cls,
        user_id: str,
        observed_state: str = "",
        interaction_history: Optional[List[str]] = None,
        upcoming_events: Optional[List[str]] = None,
        current_focus: str = "Daily routines and family",
        active_life_chapter: str = "Son's Military Service Adaptation",
        environmental_factors: Optional[EnvironmentalFactors] = None
    ) -> SituationModel:
        history = interaction_history or []
        events = upcoming_events or []
        env = environmental_factors or EnvironmentalFactors()

        hypotheses = CausalReasoningEngine.generate_hypotheses(observed_state) if observed_state else []
        routines = RoutineDetector.detect_routines(history)
        opportunities = ForecastEngine.project_support_opportunities(events)

        return SituationModel(
            user_id=user_id,
            current_focus=current_focus,
            active_life_chapter=active_life_chapter,
            hypotheses=hypotheses,
            active_routines=routines,
            support_opportunities=opportunities,
            environmental_factors=env
        )

    @classmethod
    def format_situation_prompt_context(cls, model: SituationModel) -> str:
        lines = [
            "[SITUATION & WORLD MODEL CONTEXT]",
            f"- Active Life Chapter: {model.active_life_chapter}",
            f"- Current Focus: {model.current_focus}",
            f"- Environment: {model.environmental_factors.time_of_day} | Fatigue: {model.environmental_factors.user_fatigue_level}"
        ]

        if model.hypotheses:
            lines.append("- Multi-Hypothesis Causal Explanations (Prediction != Fact):")
            for h in model.hypotheses:
                lines.append(f"  * {h.explanation} (Conf: {h.confidence:.2f})")

        if model.support_opportunities:
            lines.append("- Anticipated Support Opportunities (Gentle & Non-Coercive):")
            for opp in model.support_opportunities:
                lines.append(f"  * [{opp.title}] {opp.hedged_phrasing}")

        return "\n".join(lines)
