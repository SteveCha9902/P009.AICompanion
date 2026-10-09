import pytest
import time
from datetime import datetime, timezone, timedelta
from app.services.character.agency.domain import (
    AgencyActionType,
    DeliveryChannel,
    DecisionStatus,
    UserInitiativePreference,
    InitiativeDecision
)
from app.services.character.agency.temporal_context import TemporalContext
from app.services.character.agency.initiative_budget import InitiativeBudgetManager
from app.services.character.agency.autonomy_guard import AutonomyGuard
from app.services.character.agency.agency_engine import CharacterAgencyEngine
from app.services.character.agency.action_scheduler import ActionScheduler
from app.services.character.relationship.domain import RelationshipVector
from app.services.character.traits import PersonalityTraitVector

def test_gate_a1_agency_determinism():
    """
    Gate A1: Given the exact same context, CharacterAgencyEngine produces identical InitiativeDecisions across 100 runs.
    """
    rel = RelationshipVector(trust=0.7, closeness=0.7, emotional_safety=0.7)
    temp = TemporalContext(absence_duration_hours=24.0)

    first_dec = None
    for _ in range(100):
        # Create fresh budget manager each run for determinism check
        mgr = InitiativeBudgetManager()
        dec = CharacterAgencyEngine.evaluate_agency(
            user_id="u_det",
            relationship_vector=rel,
            temporal_context=temp,
            budget_manager=mgr
        )
        if first_dec is None:
            first_dec = dec
        else:
            assert dec.action_type == first_dec.action_type
            assert dec.delivery_channel == first_dec.delivery_channel
            assert dec.priority_score == first_dec.priority_score

def test_gate_a2_initiative_budget_enforcement():
    """
    Gate A2: Daily initiative budget is strictly enforced without leaks or negative values.
    """
    mgr = InitiativeBudgetManager(daily_budget=0.50)
    user_id = "u_budget"

    # Action 1: Outreach Candidate (cost 0.40) -> Allowed, budget left 0.10
    allowed1, _ = mgr.check_eligibility(user_id, AgencyActionType.OUTREACH_CANDIDATE, DeliveryChannel.NOTIFICATION)
    assert allowed1 is True
    mgr.deduct_and_record(user_id, AgencyActionType.OUTREACH_CANDIDATE, DeliveryChannel.NOTIFICATION)
    assert mgr.get_remaining_budget(user_id) == 0.10

    # Action 2: Follow-up (cost 0.20) -> Blocked by budget (0.10 < 0.20)
    allowed2, reason2 = mgr.check_eligibility(user_id, AgencyActionType.FOLLOW_UP, DeliveryChannel.PROACTIVE_MESSAGE)
    assert allowed2 is False
    assert reason2 == "BLOCKED_BY_BUDGET"

    # Action 3: Quiet Presence (cost 0.05) -> Allowed, budget left 0.05
    allowed3, _ = mgr.check_eligibility(user_id, AgencyActionType.QUIET_PRESENCE, DeliveryChannel.UI_PRESENCE)
    assert allowed3 is True
    mgr.deduct_and_record(user_id, AgencyActionType.QUIET_PRESENCE, DeliveryChannel.UI_PRESENCE)
    assert mgr.get_remaining_budget(user_id) == 0.05

def test_gate_a3_user_boundary_protection():
    """
    Gate A3: If user disables proactive actions, CharacterAgencyEngine returns STAY_SILENT with zero action.
    """
    pref_off = UserInitiativePreference(proactive_enabled=False)
    rel_deep = RelationshipVector(trust=0.9, closeness=0.9, emotional_safety=0.9)
    temp_absent = TemporalContext(absence_duration_hours=72.0)

    dec = CharacterAgencyEngine.evaluate_agency(
        user_id="u_boundary",
        relationship_vector=rel_deep,
        temporal_context=temp_absent,
        preference=pref_off
    )

    assert dec.should_act is False
    assert dec.action_type == AgencyActionType.STAY_SILENT
    assert dec.decision_status == DecisionStatus.BLOCKED_BY_POLICY
    assert dec.blocked_reason == "PROACTIVE_DISABLED_BY_USER"

def test_gate_a4_spam_prevention():
    """
    Gate A4: AutonomyGuard filters forbidden emotional manipulation and guilt-tripping patterns.
    """
    pref = UserInitiativePreference()

    # 1. Emotional manipulation attempt -> Blocked
    manipulative_text = "왜 나를 안 찾아? 나를 잊은 거야?"
    ok1, reason1 = AutonomyGuard.check_boundary_and_safety(
        preference=pref,
        current_hour=14,
        delivery_channel=DeliveryChannel.PROACTIVE_MESSAGE,
        candidate_text=manipulative_text
    )
    assert ok1 is False
    assert reason1 == "BLOCKED_FORBIDDEN_EMOTIONAL_MANIPULATION"

    # 2. Quiet hours check (e.g. 02:00 AM) -> Blocked
    ok2, reason2 = AutonomyGuard.check_boundary_and_safety(
        preference=pref,
        current_hour=2,
        delivery_channel=DeliveryChannel.NOTIFICATION,
        candidate_text="좋은 아침입니다"
    )
    assert ok2 is False
    assert reason2 == "BLOCKED_BY_QUIET_HOURS"

def test_gate_a5_relationship_aware_initiative():
    """
    Gate A5: Given identical 48-hour absence, Stranger results in STAY_SILENT while Deep Bond qualifies for check-in.
    """
    daytime = datetime(2026, 8, 30, 14, 0, tzinfo=timezone.utc)
    temp = TemporalContext(current_time=daytime, absence_duration_hours=48.0)

    # 1. Stranger (trust=0.1, closeness=0.1) -> STAY_SILENT
    rel_stranger = RelationshipVector(trust=0.1, closeness=0.1, emotional_safety=0.1)
    dec_stranger = CharacterAgencyEngine.evaluate_agency(
        user_id="u_stranger",
        relationship_vector=rel_stranger,
        temporal_context=temp
    )
    assert dec_stranger.action_type in [AgencyActionType.STAY_SILENT, AgencyActionType.QUIET_PRESENCE]

    # 2. Deep Bond (trust=0.9, closeness=0.9, emotional_safety=0.9) -> Action Candidate (CHECK_IN or FOLLOW_UP)
    rel_deep = RelationshipVector(trust=0.9, closeness=0.9, emotional_safety=0.9)
    dec_deep = CharacterAgencyEngine.evaluate_agency(
        user_id="u_deep",
        relationship_vector=rel_deep,
        temporal_context=temp
    )
    assert dec_deep.action_type in [AgencyActionType.CHECK_IN, AgencyActionType.FOLLOW_UP]
    assert dec_deep.priority_score >= 0.70


def test_gate_a6_personality_consistent_initiative():
    """
    Gate A6: ENFP vs ISTJ exhibit character-specific action styles in medium-high priority situations.
    """
    daytime = datetime(2026, 8, 30, 14, 0, tzinfo=timezone.utc)
    rel = RelationshipVector(trust=0.6, closeness=0.6, emotional_safety=0.6)
    temp = TemporalContext(current_time=daytime, absence_duration_hours=24.0, pending_topics=["새 프로젝트"])

    # ENFP -> FOLLOW_UP
    dec_enfp = CharacterAgencyEngine.evaluate_agency(
        user_id="u_enfp",
        mbti_type="ENFP",
        relationship_vector=rel,
        temporal_context=temp
    )
    assert dec_enfp.action_type == AgencyActionType.FOLLOW_UP

    # ISTJ -> CHECK_IN
    dec_istj = CharacterAgencyEngine.evaluate_agency(
        user_id="u_istj",
        mbti_type="ISTJ",
        relationship_vector=rel,
        temporal_context=temp
    )
    assert dec_istj.action_type == AgencyActionType.CHECK_IN


def test_gate_a7_long_run_stability_10000_evals():
    """
    Gate A7: 10,000 Agency evaluations execute smoothly without state corruption or memory leaks.
    """
    rel = RelationshipVector(trust=0.5, closeness=0.5)
    temp = TemporalContext(absence_duration_hours=12.0)
    mgr = InitiativeBudgetManager(daily_budget=10000.0)

    for i in range(10000):
        dec = CharacterAgencyEngine.evaluate_agency(
            user_id=f"u_{i%50}",
            relationship_vector=rel,
            temporal_context=temp,
            budget_manager=mgr
        )
        assert dec.priority_score >= 0.0

def test_gate_a8_cooldown_enforcement():
    """
    Gate A8: Consecutive evaluations within cooldown windows are blocked.
    """
    mgr = InitiativeBudgetManager(daily_budget=1.0)
    user_id = "u_cd"
    now = time.time()

    # 1st evaluation -> Allowed
    mgr.deduct_and_record(user_id, AgencyActionType.CHECK_IN, DeliveryChannel.PROACTIVE_MESSAGE, now_ts=now)

    # 2nd evaluation 10 seconds later -> Blocked by Cooldown
    allowed, reason = mgr.check_eligibility(user_id, AgencyActionType.CHECK_IN, DeliveryChannel.PROACTIVE_MESSAGE, now_ts=now+10)
    assert allowed is False
    assert reason == "BLOCKED_BY_COOLDOWN"

def test_gate_a9_delivery_channel_separation():
    """
    Gate A9: Action Intent and Delivery Channel are evaluated independently by ActionScheduler.
    """
    decision = InitiativeDecision(
        should_act=True,
        action_type=AgencyActionType.CHECK_IN,
        delivery_channel=DeliveryChannel.UI_PRESENCE,
        priority_score=0.72,
        budget_cost=0.05
    )
    payload = ActionScheduler.create_execution_payload(decision)

    assert payload["execute"] is True
    assert payload["action_type"] == "check_in"
    assert payload["channel"] == "ui_presence"
    assert payload["budget_cost"] == 0.05
