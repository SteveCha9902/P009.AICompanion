from typing import List, Dict, Any, Tuple
from app.domain.observability.companion_metrics import OverallCompanionQuality
from app.domain.improvement.improvement_signal import (
    ImprovementSignal,
    CorrectionPlan,
    TuningParameters,
    NonDegradationCheck
)
from app.services.improvement.quality_regression_detector import QualityRegressionDetector
from app.services.improvement.correction_planner import CorrectionPlanner
from app.services.improvement.adaptive_tuner import AdaptiveTuner

class SelfImprovementEngine:
    """
    Closed-Loop Self-Improvement Orchestrator.
    Observation -> Regression Detection -> Correction Planning -> Adaptive Tuning -> Constitution & Non-Degradation Validation.
    """

    _current_parameters = TuningParameters()

    @classmethod
    def get_current_parameters(cls) -> TuningParameters:
        return cls._current_parameters

    @classmethod
    def run_self_improvement_cycle(
        cls,
        current_quality: OverallCompanionQuality,
        simulated_usage_rate: float = 1.0
    ) -> Dict[str, Any]:
        # Step 1: Detect Regressions
        signals = QualityRegressionDetector.detect_regressions(current_quality)
        if not signals:
            return {
                "cycle_executed": False,
                "applied_plans": [],
                "parameters": cls._current_parameters,
                "message": "No quality regression detected. Operating at optimal baseline."
            }

        applied_plans: List[CorrectionPlan] = []
        logs: List[str] = []

        # Step 2: Plan and Tune
        for sig in signals:
            plan = CorrectionPlanner.create_plan_from_signal(sig, cls._current_parameters)
            if plan:
                is_ok, new_params, non_deg, msg = AdaptiveTuner.apply_plan(
                    plan=plan,
                    params=cls._current_parameters,
                    simulated_post_usage_rate=simulated_usage_rate
                )
                if is_ok and non_deg.is_capability_preserved:
                    cls._current_parameters = new_params
                    applied_plans.append(plan)
                    logs.append(msg)
                else:
                    logs.append(f"Skipped plan {plan.plan_id}: {msg}")

        return {
            "cycle_executed": len(applied_plans) > 0,
            "detected_signals_count": len(signals),
            "applied_plans": applied_plans,
            "parameters": cls._current_parameters,
            "logs": logs,
            "summary": f"Self-improvement cycle finished. Applied {len(applied_plans)} safe parameter adjustments."
        }
