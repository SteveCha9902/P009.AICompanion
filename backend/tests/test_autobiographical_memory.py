import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock

from app.domain.memory.episodic_memory import EpisodicMemory
from app.domain.memory.life_event import LifeEvent, LifeEventCategory
from app.domain.memory.shared_experience import SharedExperience
from app.domain.memory.story_chapter import StoryChapter
from app.domain.memory.timeline_event import TimelineEvent

from app.services.memory.event_importance_engine import EventImportanceEngine
from app.services.memory.life_event_promoter import LifeEventPromoter
from app.services.shared_experience.experience_linker import ExperienceLinker
from app.services.memory.autobiographical_context_compiler import AutobiographicalContextCompiler
from app.services.memory.autobiographical_narrative_service import AutobiographicalNarrativeService

def test_gate_m1_and_m2_importance_scoring_trivial_vs_milestone():
    """
    Gate M1 & M2: Episodic Importance Engine must filter routine chat and score milestones highly.
    """
    # 1. Trivial routine chat
    trivial_score = EventImportanceEngine.calculate_importance(
        summary="User said they ate lunch and are feeling a bit sleepy.",
        emotional_context={"arousal": 0.2, "valence": 0.0},
        user_input="점심 먹었어 날씨 졸려"
    )
    assert trivial_score <= 0.20, f"Trivial conversation scored too high: {trivial_score}"

    # 2. Life milestone chat
    milestone_score = EventImportanceEngine.calculate_importance(
        summary="User completed their long-running AI project and launched the first working prototype.",
        emotional_context={"arousal": 0.9, "valence": 0.8},
        user_input="프로젝트 완성하고 첫 배포 성공했어!"
    )
    assert milestone_score >= 0.75, f"Milestone scored too low: {milestone_score}"

@pytest.mark.asyncio
async def test_gate_m3_and_m4_life_event_promotion_and_duplicate_prevention():
    """
    Gate M3 & M4: High-importance episodes must be promoted to Life Events while preventing duplicates.
    """
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Configure mock execute returning empty list (first time -> promote)
    mock_res_empty = MagicMock()
    mock_res_empty.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_res_empty

    promoter = LifeEventPromoter(mock_db)

    episode = EpisodicMemory(
        user_id="user_1",
        companion_id="comp_1",
        summary="사용자가 AI 프로젝트의 첫 번째 완성 버전을 배포했다.",
        importance=0.88
    )

    life_event = await promoter.evaluate_and_promote(episode)
    assert life_event is not None
    assert life_event.category == LifeEventCategory.PROJECT_MILESTONE
    assert life_event.importance >= 0.75

    # Test Duplicate Prevention
    mock_existing = MagicMock(summary="사용자가 AI 프로젝트의 첫 번째 완성 버전을 배포했다.")
    mock_res_dup = MagicMock()
    mock_res_dup.scalars.return_value.all.return_value = [mock_existing]
    mock_db.execute.return_value = mock_res_dup

    duplicate_event = await promoter.evaluate_and_promote(episode)
    assert duplicate_event is None # Must be safely deduplicated

def test_gate_m5_experience_linking_narrative_chain():
    """
    Gate M5: ExperienceLinker must chain related milestones into a coherent story progression.
    """
    events = [
        LifeEvent(
            title="프로젝트 아이디어 시작",
            summary="새로운 AI 컴패니언 프로젝트 구상",
            category=LifeEventCategory.PROJECT_MILESTONE,
            occurred_at=datetime.utcnow() - timedelta(days=30)
        ),
        LifeEvent(
            title="기술적 난관 직면",
            summary="엔진 통합 중 아키텍처 문제로 고민",
            category=LifeEventCategory.PROJECT_MILESTONE,
            occurred_at=datetime.utcnow() - timedelta(days=15)
        ),
        LifeEvent(
            title="첫 번째 프로토타입 완성",
            summary="난관을 극복하고 첫 배포 성공",
            category=LifeEventCategory.PROJECT_MILESTONE,
            occurred_at=datetime.utcnow()
        )
    ]

    chains = ExperienceLinker.link_events(events)
    assert len(chains) == 1
    assert chains[0]["event_count"] == 3
    assert "프로젝트 아이디어 시작 ➔ 기술적 난관 직면 ➔ 첫 번째 프로토타입 완성" in chains[0]["progression"]

def test_gate_m9_and_m10_truth_boundary_context_compiler():
    """
    Gate M9 & M10: Context compiler must strictly distinguish 'our shared experience' vs 'user personal private memory'.
    """
    chapters = [
        StoryChapter(
            chapter_number=1,
            title="시작과 도전",
            theme="PROJECT",
            summary="우리가 함께 고민하며 프로젝트를 완성해 나간 시간."
        )
    ]

    shared_experiences = [
        SharedExperience(
            title="AI 프로젝트 런칭",
            summary="AI Companion 아키텍처를 함께 설계하고 구현을 완성했다.",
            is_co_experienced=True
        ),
        SharedExperience(
            title="사용자의 가족 여행",
            summary="사용자가 주말 동안 제주도 가족 여행을 다녀왔다.",
            is_co_experienced=False
        )
    ]

    compiled = AutobiographicalContextCompiler.compile(
        chapters=chapters,
        shared_experiences=shared_experiences,
        recent_life_events=[]
    )

    assert "[SHARED HISTORY & AUTOBIOGRAPHICAL MEMORY]" in compiled
    assert "Together: AI Companion 아키텍처를 함께 설계하고 구현을 완성했다." in compiled
    assert "User's Personal Event (You listened): 사용자가 주말 동안 제주도 가족 여행을 다녀왔다." in compiled
    assert "[MEMORY TRUTH BOUNDARY]" in compiled
    assert "Never fabricate false joint experiences" in compiled

def test_gate_m7_narrative_generation():
    """
    Gate M7: AutobiographicalNarrativeService generates structured retrospective story.
    """
    chapters = [
        StoryChapter(chapter_number=1, title="첫 만남", theme="START", summary="서로를 알아간 첫 대화"),
        StoryChapter(chapter_number=2, title="공동 프로젝트", theme="GROWTH", summary="아이디어를 실현한 순간")
    ]
    timeline = [TimelineEvent(title="첫 대화", summary="만남")]

    narrative = AutobiographicalNarrativeService.generate_narrative(chapters, timeline)
    assert "우리가 함께한 시간들을 돌아보면" in narrative
    assert "첫 만남" in narrative
    assert "공동 프로젝트" in narrative
