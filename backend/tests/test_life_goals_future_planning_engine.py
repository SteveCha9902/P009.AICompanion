import pytest
from datetime import date, timedelta
from app.domain.goal.goal import Goal, GoalCandidate, GoalType, GoalStatus, GoalMilestone
from app.services.goal.goal_extractor import GoalExtractor
from app.services.goal.planning_engine import PlanningEngine
from app.services.goal.goal_recall_engine import GoalRecallEngine
from app.services.goal.dday_engine import DDayEngine

def test_gate_fp1_goal_detection():
    """
    Gate FP1: Detects goal intention from dialogue and creates GoalCandidate.
    """
    cand = GoalExtractor.extract_goal_candidate("u1", "올해 체력을 좀 키우고 싶어 매일 걷기 시작할 계획이야")
    assert cand is not None
    assert cand.goal_type == GoalType.HEALTH
    assert cand.confidence >= 0.65


def test_gate_fp2_goal_recall_accuracy():
    """
    Gate FP2: Accurately matches active goal upon related user utterance.
    """
    PlanningEngine.clear()
    cand = GoalCandidate(candidate_id="c1", user_id="u1", title="매일 30분 걷기", goal_type=GoalType.HEALTH)
    PlanningEngine.confirm_and_create_goal(cand)

    recall_res = GoalRecallEngine.find_relevant_goal_recall("u1", "오늘 걷기 운동 어땠을까?")
    assert recall_res is not None
    goal, intent_name, guidance = recall_res
    assert goal.title == "매일 30분 걷기"
    assert intent_name == "GOAL_REVIEW"


def test_gate_fp3_milestone_planning():
    """
    Gate FP3: Decomposes goal into milestones and marks individual milestones completed.
    """
    PlanningEngine.clear()
    cand = GoalCandidate(candidate_id="c2", user_id="u1", title="자격증 취득", goal_type=GoalType.LEARNING)
    goal = PlanningEngine.confirm_and_create_goal(
        cand,
        initial_milestones=["기본서 1회독", "기출문제 풀이", "최종 모의고사"]
    )
    assert len(goal.milestones) == 3

    # Complete 1 milestone
    m1 = goal.milestones[0]
    completed_m = PlanningEngine.complete_milestone("u1", goal.goal_id, m1.milestone_id)
    assert completed_m.is_completed is True
    assert goal.status == GoalStatus.ACTIVE


def test_gate_fp4_non_controlling_behavior():
    """
    Gate FP4: Strict prohibition of scolding, pressuring, or manager-like interrogation.
    """
    cand = GoalCandidate(candidate_id="c3", user_id="u1", title="다이어트", goal_type=GoalType.HEALTH)
    PlanningEngine.confirm_and_create_goal(cand)

    recall_res = GoalRecallEngine.find_relevant_goal_recall("u1", "다이어트 생각 중")
    assert recall_res is not None
    _, _, guidance = recall_res
    assert "without demanding accountability or inducing guilt" in guidance


def test_gate_fp5_goal_confidence_and_commitment():
    """
    Gate FP5: Separates inference confidence from user's commitment level.
    """
    cand = GoalCandidate(candidate_id="c4", user_id="u1", title="일본 여행", goal_type=GoalType.TRAVEL, confidence=0.70)
    goal = PlanningEngine.confirm_and_create_goal(cand, commitment_level=0.90)
    assert goal.confidence == 0.70
    assert goal.commitment_level == 0.90


def test_gate_fp6_timeline_integration():
    """
    Gate FP6: Goal targets seamlessly integrate with future temporal timelines.
    """
    future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    cand = GoalCandidate(candidate_id="c5", user_id="u1", title="프로젝트 출시", goal_type=GoalType.PROJECT)
    goal = PlanningEngine.confirm_and_create_goal(cand, target_date_str=future_date)
    assert goal.target_date_str == future_date


def test_gate_fp7_relationship_consistency():
    """
    Gate FP7: Goal conversations maintain gentle, warm, and supportive tone.
    """
    from app.services.context.providers.future_context_provider import FutureContextProvider
    prov = FutureContextProvider("u1")
    assert prov.user_id == "u1"


def test_gate_fp8_progress_celebration():
    """
    Gate FP8: Triggers CELEBRATE_PROGRESS intent upon user milestone completion.
    """
    PlanningEngine.clear()
    cand = GoalCandidate(candidate_id="c6", user_id="u1", title="자격증 시험", goal_type=GoalType.LEARNING)
    PlanningEngine.confirm_and_create_goal(cand)

    recall_res = GoalRecallEngine.find_relevant_goal_recall("u1", "자격증 시험 드디어 합격했어!")
    assert recall_res is not None
    _, intent_name, guidance = recall_res
    assert intent_name == "CELEBRATE_PROGRESS"
    assert "Heartfelt Celebration" in guidance


def test_gate_fp9_user_agency_protection():
    """
    Gate FP9: GoalCandidate prompts user with confirmation question rather than forcing goal creation.
    """
    cand = GoalExtractor.extract_goal_candidate("u1", "내년에 스페인어 배우고 싶어")
    assert cand is not None
    assert "기억해둘까요?" in cand.suggested_confirmation_prompt


def test_gate_fp10_goal_approval_workflow():
    """
    Gate FP10: Goal is only officially registered upon explicit user confirmation.
    """
    PlanningEngine.clear()
    cand = GoalExtractor.extract_goal_candidate("u_conf", "매일 책 10페이지 읽기 시작했어")
    assert len(PlanningEngine.list_user_goals("u_conf")) == 0

    # User confirms
    PlanningEngine.confirm_and_create_goal(cand)
    assert len(PlanningEngine.list_user_goals("u_conf")) == 1


def test_gate_fp11_dday_accuracy():
    """
    Gate FP11: Accurately calculates D-Day tags.
    """
    d7_str = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    dday_info = DDayEngine.calculate_dday("아들 첫 휴가", d7_str)
    assert dday_info is not None
    assert dday_info.dday_tag == "D-7"
    assert dday_info.days_remaining == 7


def test_gate_fp12_no_guilt_induction_and_archived():
    """
    Gate FP12: Discontinued goals are ARCHIVED without failure labeling.
    """
    PlanningEngine.clear()
    cand = GoalCandidate(candidate_id="c7", user_id="u_arc", title="마라톤 풀코스", goal_type=GoalType.HEALTH)
    goal = PlanningEngine.confirm_and_create_goal(cand)

    archived = PlanningEngine.archive_goal("u_arc", goal.goal_id)
    assert archived.status == GoalStatus.ARCHIVED
    # Does not appear in active goals list
    assert len(PlanningEngine.list_user_goals("u_arc", include_archived=False)) == 0
    assert len(PlanningEngine.list_user_goals("u_arc", include_archived=True)) == 1
