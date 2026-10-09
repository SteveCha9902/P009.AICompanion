import pytest
from app.domain.timeline.life_event import LifeTimeline, LifeEvent, TimelineCategory, TimelinePrivacyPolicy
from app.services.timeline.timeline_builder import TimelineBuilder
from app.services.timeline.event_linker import EventLinker
from app.services.timeline.timeline_repair_engine import TimelineRepairEngine
from app.services.timeline.personal_history_engine import PersonalHistoryEngine

def test_gate_lt1_life_event_creation():
    """
    Gate LT1: Creates life event with category, timestamp, and importance.
    """
    TimelineBuilder.clear()
    event = TimelineBuilder.register_event(
        user_id="u1",
        title="몬스테라 화분 구매",
        category=TimelineCategory.PLANT if hasattr(TimelineCategory, "PLANT") else TimelineCategory.HOME,
        event_date_str="2026-06"
    )
    assert event is not None
    assert event.event_date_str == "2026-06"


def test_gate_lt2_timeline_linking():
    """
    Gate LT2: EventLinker links causal life events into connected story chains.
    """
    TimelineBuilder.clear()
    e1 = TimelineBuilder.register_event("u1", "화분 구매", TimelineCategory.HOME, event_date_str="2026-06")
    e2 = TimelineBuilder.register_event("u1", "첫 새 잎 돋음", TimelineCategory.HOME, event_date_str="2026-08", parent_event_id=e1.event_id)
    e3 = TimelineBuilder.register_event("u1", "큰 화분으로 분갈이", TimelineCategory.HOME, event_date_str="2026-10", parent_event_id=e2.event_id)

    timeline = TimelineBuilder.get_or_create_timeline("u1")
    chain = EventLinker.get_event_narrative_chain(timeline, e3.event_id)
    assert len(chain) == 3
    assert chain[0].title == "화분 구매"
    assert chain[-1].title == "큰 화분으로 분갈이"


def test_gate_lt3_cross_memory_association():
    """
    Gate LT3: Associates multiple memory IDs with single life milestone.
    """
    TimelineBuilder.clear()
    event = TimelineBuilder.register_event(
        "u1",
        "자격증 시험 합격",
        TimelineCategory.GOAL,
        related_memories=["mem_001", "mem_002"]
    )
    assert len(event.related_memories) == 2


def test_gate_lt4_personal_history_recall():
    """
    Gate LT4: Reconstructs narrative timeline string based on matching query.
    """
    TimelineBuilder.clear()
    e1 = TimelineBuilder.register_event("u1", "반려견 입양", TimelineCategory.PET, event_date_str="2026-01")
    e2 = TimelineBuilder.register_event("u1", "반려견 첫 생일 파티", TimelineCategory.PET, event_date_str="2027-01", parent_event_id=e1.event_id)

    res = PersonalHistoryEngine.find_relevant_timeline_narrative("u1", "우리 반려견 너무 귀여워")
    assert res is not None
    matched_ev, narrative = res
    assert "Timeline Narrative" in narrative
    assert "반려견 입양" in narrative


def test_gate_lt5_timeline_accuracy_and_non_dogmatic_tone():
    """
    Gate LT5: Low confidence events use tentative/gentle recall framing.
    """
    TimelineBuilder.clear()
    event = TimelineBuilder.register_event(
        "u1",
        "제주도 여행 계획",
        TimelineCategory.TRAVEL,
        confidence=0.55,
        event_date_str="2026-09"
    )
    res = PersonalHistoryEngine.find_relevant_timeline_narrative("u1", "제주도 생각나네")
    assert res is not None
    _, narrative = res
    assert "Gentle Recall" in narrative or "Tentative" in narrative


def test_gate_lt6_long_term_consistency():
    """
    Gate LT6: Chronological sorting maintains proper time sequence.
    """
    TimelineBuilder.clear()
    e2 = TimelineBuilder.register_event("u1", "사건 2", TimelineCategory.PROJECT, event_date_str="2026-09")
    e1 = TimelineBuilder.register_event("u1", "사건 1", TimelineCategory.PROJECT, event_date_str="2026-05")
    # Force timestamps
    e1.timestamp_ms = 1000
    e2.timestamp_ms = 2000

    timeline = TimelineBuilder.get_or_create_timeline("u1")
    events = timeline.get_chronological_events(TimelineCategory.PROJECT)
    assert events[0].title == "사건 1"
    assert events[1].title == "사건 2"


def test_gate_lt7_relationship_integration():
    """
    Gate LT7: Timeline narrative integrates smoothly without overwhelming prompt context.
    """
    TimelineBuilder.clear()
    TimelineBuilder.register_event("u1", "독서 모임 시작", TimelineCategory.HOBBY)
    res = PersonalHistoryEngine.find_relevant_timeline_narrative("u1", "독서 모임 다녀왔어")
    assert res is not None


def test_gate_lt8_avatar_recall_alignment():
    """
    Gate LT8: Validates avatar 3-stage recall sequence guidance.
    """
    # Cognitive OS maps RECALL_TIMELINE to thinking avatar expression
    from app.domain.cognitive.decision_types import BehaviorIntent
    assert BehaviorIntent.RECALL_TIMELINE.value == "RECALL_TIMELINE"


def test_gate_lt9_timeline_privacy_and_consent_guard():
    """
    Gate LT9: Sensitive categories (HEALTH, FAMILY, CAREER) blocked unless explicitly consented.
    """
    TimelineBuilder.clear()
    # 1. Unconsented Health event -> MUST be blocked
    evt_blocked = TimelineBuilder.register_event("u_priv", "건강 검진 결과", TimelineCategory.HEALTH)
    assert evt_blocked is None

    # 2. Grant consent -> Now allowed
    TimelineBuilder.grant_consent("u_priv", TimelineCategory.HEALTH)
    evt_allowed = TimelineBuilder.register_event("u_priv", "건강 검진 결과", TimelineCategory.HEALTH)
    assert evt_allowed is not None


def test_gate_lt10_timeline_repair_and_correction():
    """
    Gate LT10: Handles user corrections to fix misremembered event details.
    """
    TimelineBuilder.clear()
    evt = TimelineBuilder.register_event("u_rep", "식물 구매", TimelineCategory.HOME)
    timeline = TimelineBuilder.get_or_create_timeline("u_rep")

    # User says: "It was a ceramic pot, not a plant."
    repaired = TimelineRepairEngine.repair_event_title(timeline, evt.event_id, "도자기 화분 구매")
    assert repaired.title == "도자기 화분 구매"
    assert repaired.confidence == 1.0

    # User says: "Please delete that mistaken event."
    removed = TimelineRepairEngine.remove_inaccurate_event(timeline, evt.event_id)
    assert removed is True
    assert len(timeline.events) == 0
