from typing import Dict, List, Optional
import time
from app.domain.identity.identity_state import LifeChapter
from app.domain.timeline.life_event import LifeEvent

class LifeChapterBuilder:
    """
    Synthesizes atomic LifeEvents into thematic multi-month/multi-year LifeChapters.
    e.g. "아들 군 복무" (입대 -> 훈련소 -> 자대 -> 외박 -> 전역)
    """

    _chapters: Dict[str, List[LifeChapter]] = {} # user_id -> chapters

    @classmethod
    def create_or_update_chapter(
        cls,
        user_id: str,
        title: str,
        category: str,
        start_date_str: str,
        events: List[LifeEvent],
        summary_narrative: str = "",
        is_ongoing: bool = True
    ) -> LifeChapter:
        if user_id not in cls._chapters:
            cls._chapters[user_id] = []

        existing = next((c for c in cls._chapters[user_id] if c.title == title), None)
        event_ids = [e.event_id for e in events]

        if not summary_narrative:
            summary_narrative = f"'{title}' 챕터: {len(events)}개의 소중한 순간들이 함께 이어지고 있습니다."

        if existing:
            existing.event_ids = list(set(existing.event_ids + event_ids))
            existing.summary_narrative = summary_narrative
            existing.is_ongoing = is_ongoing
            existing.updated_at_ms = int(time.time() * 1000)
            return existing

        chapter = LifeChapter(
            chapter_id=f"chap_{int(time.time()*1000)}",
            user_id=user_id,
            title=title,
            category=category,
            start_date_str=start_date_str,
            event_ids=event_ids,
            summary_narrative=summary_narrative,
            is_ongoing=is_ongoing
        )
        cls._chapters[user_id].append(chapter)
        return chapter

    @classmethod
    def list_chapters(cls, user_id: str) -> List[LifeChapter]:
        return cls._chapters.get(user_id, [])

    @classmethod
    def clear(cls) -> None:
        cls._chapters.clear()
