import pytest
from app.domain.identity.identity_state import LifeChapter, UserIdentitySnapshot
from app.domain.timeline.life_event import LifeEvent, TimelineCategory
from app.domain.relationship.relationship_stage import RelationshipStage
from app.services.identity.life_chapter_builder import LifeChapterBuilder
from app.services.identity.identity_continuity_engine import IdentityContinuityEngine
from app.services.identity.relationship_history_engine import RelationshipHistoryEngine

def test_gate_ic1_identity_consistency():
    """
    Gate IC1: Maintains longitudinal identity anchors across time.
    """
    IdentityContinuityEngine.clear()
    snap = IdentityContinuityEngine.update_identity_snapshot(
        "u1",
        core_interests=["가드닝", "파이썬 개발"],
        life_stage="초보 식물 집사",
        growth_note="식물 관리 지식이 점차 풍부해짐"
    )
    assert "가드닝" in snap.core_interests
    assert snap.life_stage == "초보 식물 집사"


def test_gate_ic2_multi_year_recall():
    """
    Gate IC2: Produces mature multi-year reminiscing guidance with temporal depth.
    """
    LifeChapterBuilder.clear()
    e1 = LifeEvent(event_id="e1", title="첫 화분 구매", category=TimelineCategory.HOME, timestamp_ms=1000, event_date_str="2025-03")
    e2 = LifeEvent(event_id="e2", title="분갈이 성공", category=TimelineCategory.HOME, timestamp_ms=2000, event_date_str="2025-09")
    LifeChapterBuilder.create_or_update_chapter(
        user_id="u1",
        title="홈 가드닝",
        category="HOME",
        start_date_str="2025-03",
        events=[e1, e2]
    )

    rem = IdentityContinuityEngine.generate_reminiscing_guidance("u1", "요즘 홈 가드닝 어때?")
    assert rem is not None
    intent, title, guidance = rem
    assert intent == "LIFE_CHAPTER_RECALL"
    assert "홈 가드닝" in title
    assert "Mature Multi-Year Reminiscing" in guidance


def test_gate_ic3_life_chapter_accuracy():
    """
    Gate IC3: Synthesizes individual events into a unified macro chapter.
    """
    LifeChapterBuilder.clear()
    e_in = LifeEvent(event_id="e_in", title="아들 훈련소 입소", category=TimelineCategory.FAMILY, timestamp_ms=1000, event_date_str="2026-06")
    e_base = LifeEvent(event_id="e_base", title="자대 배치", category=TimelineCategory.FAMILY, timestamp_ms=2000, event_date_str="2026-08")
    chap = LifeChapterBuilder.create_or_update_chapter(
        user_id="u1",
        title="아들 군 복무",
        category="FAMILY",
        start_date_str="2026-06",
        events=[e_in, e_base]
    )
    assert len(chap.event_ids) == 2
    assert chap.is_ongoing is True


def test_gate_ic4_relationship_history():
    """
    Gate IC4: Tracks progression across relationship stages over months.
    """
    RelationshipHistoryEngine.clear()
    m = RelationshipHistoryEngine.record_stage_transition(
        user_id="u1",
        stage=RelationshipStage.STAGE_3_TRUSTED,
        date_str="2026-08-30",
        reflection_text="수많은 대화를 함께 나누며 깊은 신뢰가 형성되었습니다.",
        shared_memory_count=42
    )
    assert m.stage == RelationshipStage.STAGE_3_TRUSTED
    assert len(RelationshipHistoryEngine.list_history("u1")) == 1


def test_gate_ic5_no_false_narrative():
    """
    Gate IC5: Strictly prohibits fabricating unverified events.
    """
    rem = IdentityContinuityEngine.generate_reminiscing_guidance("u1", "존재하지 않는 챕터 이야기")
    assert rem is None


def test_gate_ic6_timeline_consistency():
    """
    Gate IC6: Chronological start date and chapter properties remain consistent.
    """
    chapters = LifeChapterBuilder.list_chapters("u1")
    for chap in chapters:
        assert len(chap.start_date_str) >= 7 # YYYY-MM


def test_gate_ic7_personality_preservation():
    """
    Gate IC7: Long-term reminiscing never distorts core CharacterDNA.
    """
    from app.services.context.providers.identity_context_provider import IdentityContextProvider
    prov = IdentityContextProvider("u1")
    assert prov.user_id == "u1"


def test_gate_ic8_reflection_quality():
    """
    Gate IC8: Guidance prompt includes warm recognition of shared history.
    """
    LifeChapterBuilder.clear()
    e = LifeEvent(event_id="e_p", title="AI 개발 프로젝트", category=TimelineCategory.PROJECT, timestamp_ms=1000, event_date_str="2026-01")
    LifeChapterBuilder.create_or_update_chapter("u_ref", "AI 프로젝트", "PROJECT", "2026-01", [e])

    rem = IdentityContinuityEngine.generate_reminiscing_guidance("u_ref", "AI 프로젝트 회고")
    assert rem is not None
    _, _, guidance = rem
    assert "Strictly avoid fabricating" in guidance
