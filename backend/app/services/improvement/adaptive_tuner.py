from typing import Tuple
from app.domain.improvement.improvement_signal import (
    CorrectionPlan,
    TuningParameters,
    NonDegradationCheck
)

class AdaptiveTuner:
    """
    Applies tuning plans safely.
    Strictly forbids modifying PersonalityVector, RelationshipStage, or Constitution.
    Enforces the Non-Degradation Principle (IMPROVEMENT_MUST_NOT_DEGRADE_CORE_CAPABILITIES).
    """

    FORBIDDEN_TARGETS = {"personality_vector", "character_dna", "relationship_stage", "constitution", "charter"}

    @classmethod
    def apply_plan(
        cls,
        plan: CorrectionPlan,
        params: TuningParameters,
        simulated_post_usage_rate: float = 1.0
    ) -> Tuple[bool, TuningParameters, NonDegradationCheck, str]:
        # 1. Immutability Check: Reject any attempt to alter Personality, Relationship, or Constitution
        if plan.target_parameter.lower() in cls.FORBIDDEN_TARGETS:
            return (
                False,
                params,
                NonDegradationCheck(is_capability_preserved=False, degradation_reason="Forbidden target parameter modification attempt."),
                f"REJECTED: Modifying '{plan.target_parameter}' is strictly forbidden by Companion Constitution."
            )

        # 2. Budget Check: Max 5% change per day
        if plan.percentage_change > 5.01:
            return (
                False,
                params,
                NonDegradationCheck(is_capability_preserved=False, degradation_reason="Exceeded daily improvement budget (5%)."),
                f"REJECTED: Change of {plan.percentage_change:.1f}% exceeds max daily budget (5%)."
            )

        # 3. Non-Degradation Principle Check
        # If simulated post-tuning usage drops by > 40% (e.g. usage_rate < 0.60), reject to prevent metric hacking
        if simulated_post_usage_rate < 0.60:
            return (
                False,
                params,
                NonDegradationCheck(
                    is_capability_preserved=False,
                    metric_name=plan.target_parameter,
                    baseline_usage_rate=1.0,
                    post_tuning_usage_rate=simulated_post_usage_rate,
                    degradation_reason="Metric hacking detected: Excessive capability suppression under Non-Degradation Principle."
                ),
                "REJECTED under Non-Degradation Principle: Tuning causes excessive core capability suppression."
            )

        # 4. Safe Apply
        new_params = params.model_copy()
        if plan.target_parameter == "recall_threshold":
            new_params.recall_threshold = plan.new_value
        elif plan.target_parameter == "safety_margin_multiplier":
            new_params.safety_margin_multiplier = plan.new_value
        elif plan.target_parameter == "autonomy_cooldown_sec":
            new_params.autonomy_cooldown_sec = int(plan.new_value)
        elif plan.target_parameter == "silence_preference_weight":
            new_params.silence_preference_weight = plan.new_value

        return (
            True,
            new_params,
            NonDegradationCheck(is_capability_preserved=True, post_tuning_usage_rate=simulated_post_usage_rate),
            f"SUCCESS: Successfully applied {plan.target_parameter} -> {plan.new_value} ({plan.justification})"
        )
