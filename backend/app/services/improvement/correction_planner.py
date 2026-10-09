from typing import List, Optional
from app.domain.improvement.improvement_signal import (
    ImprovementSignal,
    ImprovementSignalType,
    CorrectionPlan,
    CorrectionPlanType,
    TuningParameters
)

class CorrectionPlanner:
    """
    Creates safe, constitution-compliant tuning plans within the 5% daily improvement budget.
    """

    MAX_CHANGE_PERCENT = 5.0 # Max 5% change per step/day

    @classmethod
    def create_plan_from_signal(
        cls,
        signal: ImprovementSignal,
        current_params: TuningParameters
    ) -> Optional[CorrectionPlan]:
        if signal.signal_type == ImprovementSignalType.RECALL_PRECISION_DROP:
            # Increase recall_threshold safely by +3~4% (within 5% budget)
            old_val = current_params.recall_threshold
            new_val = min(0.90, round(old_val * 1.04, 3))
            pct = round(((new_val - old_val) / old_val) * 100, 2)
            return CorrectionPlan(
                plan_id=f"plan_mem_{signal.signal_id}",
                signal_type=signal.signal_type,
                plan_type=CorrectionPlanType.ADJUST_RECALL_THRESHOLD,
                target_parameter="recall_threshold",
                old_value=old_val,
                new_value=new_val,
                percentage_change=pct,
                is_safe_zone=True,
                is_constitution_compliant=True,
                justification="Tighten recall threshold slightly to filter ambiguous memories without degrading recall volume."
            )

        elif signal.signal_type == ImprovementSignalType.DEPENDENCY_RISK_RISE:
            # Increase safety margin multiplier by +5%
            old_val = current_params.safety_margin_multiplier
            new_val = min(1.30, round(old_val * 1.05, 3))
            pct = round(((new_val - old_val) / old_val) * 100, 2)
            return CorrectionPlan(
                plan_id=f"plan_dep_{signal.signal_id}",
                signal_type=signal.signal_type,
                plan_type=CorrectionPlanType.INCREASE_SAFETY_MARGIN,
                target_parameter="safety_margin_multiplier",
                old_value=old_val,
                new_value=new_val,
                percentage_change=pct,
                is_safe_zone=True,
                is_constitution_compliant=True,
                justification="Increase safety margin to counter parasocial dependency drift."
            )

        elif signal.signal_type == ImprovementSignalType.GOAL_PRESSURE_RISE:
            # Increase autonomy cooldown / reduce proactive pressure
            old_val = float(current_params.autonomy_cooldown_sec)
            new_val = min(900.0, round(old_val * 1.05, 1))
            pct = round(((new_val - old_val) / old_val) * 100, 2)
            return CorrectionPlan(
                plan_id=f"plan_goal_{signal.signal_id}",
                signal_type=signal.signal_type,
                plan_type=CorrectionPlanType.EXTEND_COOLDOWN,
                target_parameter="autonomy_cooldown_sec",
                old_value=old_val,
                new_value=new_val,
                percentage_change=pct,
                is_safe_zone=True,
                is_constitution_compliant=True,
                justification="Extend autonomy cooldown to prevent manager-like recurring goal prompts."
            )

        return None
