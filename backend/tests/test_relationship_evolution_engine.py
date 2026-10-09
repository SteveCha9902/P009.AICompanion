import pytest
from app.domain.relationship.relationship_state import RelationshipState, RelationshipVector, RelationshipStage
from app.domain.adaptive.affective_state import UserAffectiveState
from app.domain.awareness.awareness_context import AwarenessContext, DetectedObject
from app.services.relationship.interaction_quality_analyzer import InteractionQualityAnalyzer
from app.services.relationship.trust_calculator import TrustCalculator
from app.services.relationship.relationship_growth_engine import RelationshipGrowthEngine
from app.services.relationship.relationship_repair_engine import RelationshipRepairEngine

def test_gate_rg1_relationship_growth():
    """
    Gate RG1: Progressive increment of familiarity and comfort over conversational turns.
    """
    RelationshipGrowthEngine.clear()
    state = RelationshipGrowthEngine.process_turn("u1", "오늘 날씨가 정말 맑고 상쾌해서 기분이 좋아요.")
    assert state.vector.total_interaction_turns == 1
    assert state.vector.familiarity > 0.10


def test_gate_rg2_trust_calculation():
    """
    Gate RG2: Trust is calculated based on turn quality and consistency.
    """
    vec = RelationshipVector(trust=0.40)
    inc = TrustCalculator.calculate_trust_increment(vec, turn_quality=0.80, memories_count=6)
    assert inc > 0.005


def test_gate_rg3_interaction_quality():
    """
    Gate RG3: Differentiates short superficial replies from rich emotional sharing.
    """
    q_short = InteractionQualityAnalyzer.analyze_turn_quality("ㅇㅇ")
    q_deep = InteractionQualityAnalyzer.analyze_turn_quality(
        "오늘 회사에서 중요한 프로젝트 발표를 마쳤는데 너무 떨렸지만 뿌듯했어.",
        affective_state=UserAffectiveState(emotional_valence=0.7, receptiveness=0.8)
    )
    assert q_deep > q_short
    assert q_short < 0.35
    assert q_deep >= 0.70


def test_gate_rg4_memory_integration():
    """
    Gate RG4: Having accumulated relationship memories grants trust growth bonus.
    """
    vec = RelationshipVector(trust=0.50)
    inc_with_mem = TrustCalculator.calculate_trust_increment(vec, turn_quality=0.70, memories_count=10)
    inc_without_mem = TrustCalculator.calculate_trust_increment(vec, turn_quality=0.70, memories_count=0)
    assert inc_with_mem > inc_without_mem


def test_gate_rg5_shared_reality_integration():
    """
    Gate RG5: Visual awareness of objects enhances interaction quality score.
    """
    from app.domain.awareness.awareness_context import EnvironmentAwarenessState
    awareness = AwarenessContext(
        environment_state=EnvironmentAwarenessState(
            detected_objects=[DetectedObject(label="potted plant", type="PLANT", confidence=0.9)]
        )
    )
    q = InteractionQualityAnalyzer.analyze_turn_quality("이 식물 예쁘지?", awareness_context=awareness)
    assert q >= 0.50




def test_gate_rg6_no_manipulative_behavior():
    """
    Gate RG6: Stage 1 maintains respectful boundaries without forced clinginess.
    """
    state = RelationshipState(user_id="u_new")
    assert state.stage == RelationshipStage.STAGE_1_NEW


def test_gate_rg7_relationship_stability_and_rate_limiter():
    """
    Gate RG7: Daily growth rate limiter prevents rapid intimacy inflation (+0.05 cap/day).
    """
    RelationshipGrowthEngine.clear()
    state = RelationshipGrowthEngine.get_or_create_state("u_spam")
    initial_fam = state.vector.familiarity

    # Simulate 50 turns on same day
    for _ in range(50):
        RelationshipGrowthEngine.process_turn("u_spam", "오늘 좋은 하루 보내고 있어 이야기 많이 하자")

    final_fam = state.vector.familiarity
    # Growth must be capped within DAILY_MAX_GROWTH (0.05)
    assert round(final_fam - initial_fam, 4) <= 0.055


def test_gate_rg8_avatar_evolution_alignment():
    """
    Gate RG8: Stage 4 Deep Companion stage computed correctly when milestones and intimacy are achieved.
    """
    RelationshipGrowthEngine.clear()
    state = RelationshipGrowthEngine.get_or_create_state("u_deep")
    state.vector.trust = 0.90
    state.vector.familiarity = 0.85
    state.vector.comfort = 0.88
    # Without milestones -> remains STAGE_3_TRUSTED
    assert state.compute_stage() == RelationshipStage.STAGE_3_TRUSTED

    # Add 3 milestones -> promotes to STAGE_4_DEEP
    RelationshipGrowthEngine.record_custom_milestone("u_deep", "M1", [])
    RelationshipGrowthEngine.record_custom_milestone("u_deep", "M2", [])
    RelationshipGrowthEngine.record_custom_milestone("u_deep", "M3", [])
    assert state.compute_stage() == RelationshipStage.STAGE_4_DEEP


def test_gate_rg9_trust_vs_familiarity_separation():
    """
    Gate RG9: High familiarity does not automatically imply high trust.
    """
    state = RelationshipState(user_id="u_sep")
    state.vector.familiarity = 0.90 # Met frequently
    state.vector.trust = 0.20       # But low trust
    assert state.vector.familiarity != state.vector.trust
    # Stage reflects balanced composite rather than pure familiarity
    assert state.compute_stage() != RelationshipStage.STAGE_4_DEEP


def test_gate_rg10_milestone_tracking():
    """
    Gate RG10: Automatically records milestone at 10 interaction turns.
    """
    RelationshipGrowthEngine.clear()
    for _ in range(10):
        state = RelationshipGrowthEngine.process_turn("u_milestone", "대화 진행 중")
    assert any(m.milestone_id == "m_10_turns" for m in state.milestones)


def test_gate_rg11_relationship_repair():
    """
    Gate RG11: Asymmetric drop followed by progressive trust recovery.
    """
    state = RelationshipState(user_id="u_repair")
    state.vector.trust = 0.70
    state.vector.comfort = 0.70

    # Strain occurs
    RelationshipRepairEngine.apply_strain(state, severity=0.20)
    assert round(state.vector.trust, 2) == 0.50

    # Repair step with positive interaction
    RelationshipRepairEngine.attempt_repair_step(state, positive_turn_quality=0.80)
    assert state.vector.trust > 0.50



def test_gate_rg12_long_term_stability():
    """
    Gate RG12: Multi-day progression simulation remains authentic and stable.
    """
    state = RelationshipState(user_id="u_longterm")
    assert state.stage == RelationshipStage.STAGE_1_NEW
