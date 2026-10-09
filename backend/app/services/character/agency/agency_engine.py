from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.services.character.agency.domain import (
    AgencyActionType,
    DeliveryChannel,
    DecisionStatus,
    InitiativeDecision,
    UserInitiativePreference
)
from app.services.character.agency.temporal_context import TemporalContext
from app.services.character.agency.initiative_budget import InitiativeBudgetManager
from app.services.character.agency.autonomy_guard import AutonomyGuard
from app.services.character.relationship.domain import RelationshipVector
from app.services.character.traits import PersonalityTraitVector

class CharacterAgencyEngine:
    """
    Evaluates internal character state and temporal context to make principled autonomous action decisions.
    """

    @classmethod
    def evaluate_agency(
        cls,
        user_id: str = "default_user",
        companion_id: str = "genie",
        mbti_type: str = "ENFP",
        core_traits: Optional[PersonalityTraitVector] = None,
        relationship_vector: Optional[RelationshipVector] = None,
        temporal_context: Optional[TemporalContext] = None,
        emotion_state: Optional[Dict[str, Any]] = None,
        preference: Optional[UserInitiativePreference] = None,
        budget_manager: Optional[InitiativeBudgetManager] = None
    ) -> InitiativeDecision:
        pref = preference or UserInitiativePreference()
        temp = temporal_context or TemporalContext.create()
        rel = relationship_vector or RelationshipVector()
        traits = core_traits or PersonalityTraitVector()
        budget_mgr = budget_manager or InitiativeBudgetManager()

        # 1. Hard Gate: User Proactive Disabled
        if not pref.proactive_enabled:
            return InitiativeDecision(
                should_act=False,
                action_type=AgencyActionType.STAY_SILENT,
                delivery_channel=DeliveryChannel.NONE,
                decision_status=DecisionStatus.BLOCKED_BY_POLICY,
                blocked_reason="PROACTIVE_DISABLED_BY_USER",
                reason="Proactive action explicitly disabled by user"
            )

        # 2. Compute Weighted BaseScore
        # Personality Alignment (Initiative / Curiosity)
        p_align = traits.curiosity * 0.5 + traits.warmth * 0.5
        # Relationship Relevance (Trust & Emotional Safety)
        r_relevance = rel.trust * 0.4 + rel.closeness * 0.3 + rel.emotional_safety * 0.3
        # Temporal Relevance (Absence Duration)
        t_relevance = min(1.0, temp.absence_duration_hours / 48.0)
        # Emotional Need
        e_need = 0.5
        if emotion_state and "valence" in emotion_state:
            e_need = max(0.2, abs(emotion_state["valence"]))
        # Memory Significance
        m_significance = 0.5 if len(temp.pending_topics) > 0 else 0.2

        base_score = (
            (0.20 * p_align) +
            (0.25 * r_relevance) +
            (0.20 * t_relevance) +
            (0.20 * e_need) +
            (0.15 * m_significance)
        )
        base_score = round(max(0.0, min(1.0, base_score)), 3)

        # 3. Determine Action Intent & Delivery Channel by Score Tiers
        mbti_upper = mbti_type.upper().strip()

        if base_score < 0.40:
            # Low Score -> STAY_SILENT
            return InitiativeDecision(
                should_act=False,
                action_type=AgencyActionType.STAY_SILENT,
                delivery_channel=DeliveryChannel.NONE,
                priority_score=base_score,
                decision_status=DecisionStatus.CREATED,
                reason="BaseScore below threshold; staying silent."
            )

        elif base_score < 0.58:
            # Medium-Low Score -> QUIET_PRESENCE
            action_type = AgencyActionType.QUIET_PRESENCE
            delivery_channel = DeliveryChannel.UI_PRESENCE
            cost = 0.05
            reason = "Moderate relevance; adopting quiet supportive presence on next UI open."

        elif base_score < 0.75:
            # Medium-High Score -> UI_INITIATIVE
            if mbti_upper == "ENFP":
                action_type = AgencyActionType.FOLLOW_UP
            elif mbti_upper == "ISTJ":
                action_type = AgencyActionType.CHECK_IN
            else:
                action_type = AgencyActionType.GREETING
            
            delivery_channel = DeliveryChannel.PROACTIVE_MESSAGE
            cost = 0.20
            reason = f"High relevance; initiating in-app {action_type.value} tailored for {mbti_upper} disposition."

        else:
            # High Score (0.75+) -> OUTREACH_CANDIDATE (Candidate for Outreach)
            if rel.closeness >= 0.70:
                action_type = AgencyActionType.CHECK_IN
            else:
                action_type = AgencyActionType.FOLLOW_UP

            delivery_channel = DeliveryChannel.NOTIFICATION
            cost = 0.40
            reason = "Very high relevance and significant absence; qualified as outreach candidate."


        # 4. Autonomy Guard Check
        current_hour = temp.current_time.hour
        guard_ok, guard_reason = AutonomyGuard.check_boundary_and_safety(
            preference=pref,
            current_hour=current_hour,
            delivery_channel=delivery_channel
        )
        if not guard_ok:
            # Demote or Block
            if delivery_channel == DeliveryChannel.NOTIFICATION:
                delivery_channel = DeliveryChannel.UI_PRESENCE
                cost = 0.05
                action_type = AgencyActionType.QUIET_PRESENCE
            else:
                return InitiativeDecision(
                    should_act=False,
                    action_type=AgencyActionType.STAY_SILENT,
                    delivery_channel=DeliveryChannel.NONE,
                    priority_score=base_score,
                    decision_status=DecisionStatus.BLOCKED_BY_POLICY,
                    blocked_reason=guard_reason,
                    reason=f"Blocked by AutonomyGuard ({guard_reason})"
                )

        # 5. Initiative Budget & Cooldown Check
        eligible, block_reason = budget_mgr.check_eligibility(
            user_id=user_id,
            action_type=action_type,
            delivery_channel=delivery_channel
        )
        if not eligible:
            status = DecisionStatus.BLOCKED_BY_BUDGET if block_reason == "BLOCKED_BY_BUDGET" else DecisionStatus.BLOCKED_BY_COOLDOWN
            return InitiativeDecision(
                should_act=False,
                action_type=AgencyActionType.STAY_SILENT,
                delivery_channel=DeliveryChannel.NONE,
                priority_score=base_score,
                decision_status=status,
                blocked_reason=block_reason,
                reason=f"Action blocked by budget/cooldown manager ({block_reason})"
            )

        # 6. Deduct Budget & Final Decision
        budget_mgr.deduct_and_record(
            user_id=user_id,
            action_type=action_type,
            delivery_channel=delivery_channel
        )

        return InitiativeDecision(
            should_act=True,
            action_type=action_type,
            delivery_channel=delivery_channel,
            priority_score=base_score,
            initiative_strength=round(base_score * 0.9, 2),
            timing=datetime.now(timezone.utc),
            reason=reason,
            personality_alignment=round(p_align, 2),
            relationship_alignment=round(r_relevance, 2),
            budget_cost=cost,
            decision_status=DecisionStatus.SCHEDULED
        )
