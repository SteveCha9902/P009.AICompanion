import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.models.autobiographical_memory import (
    SharedExperienceModel,
    StoryChapterModel,
    TimelineEventModel,
    LifeEventModel
)
from app.domain.memory.shared_experience import SharedExperience
from app.domain.memory.story_chapter import StoryChapter
from app.domain.memory.timeline_event import TimelineEvent
from app.domain.memory.life_event import LifeEvent, LifeEventCategory

logger = logging.getLogger(__name__)

class SharedExperienceEngine:
    """
    Manages Shared Experiences, Story Chapters, and Shared Life Timeline.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_shared_experience(
        self,
        user_id: str,
        companion_id: str,
        title: str,
        summary: str,
        is_co_experienced: bool = True
    ) -> SharedExperience:
        stmt = (
            select(SharedExperienceModel)
            .where(
                SharedExperienceModel.user_id == user_id,
                SharedExperienceModel.companion_id == companion_id,
                SharedExperienceModel.title == title
            )
        )
        res = await self.db.execute(stmt)
        model = res.scalars().first()

        if not model:
            model = SharedExperienceModel(
                user_id=user_id,
                companion_id=companion_id,
                title=title,
                summary=summary,
                is_co_experienced=is_co_experienced,
                companion_involvement_level=0.85 if is_co_experienced else 0.3,
                importance=0.85
            )
            self.db.add(model)
            await self.db.commit()
            await self.db.refresh(model)

            # Also add to Timeline
            timeline_ev = TimelineEventModel(
                user_id=user_id,
                companion_id=companion_id,
                title=title,
                summary=summary,
                importance=0.85,
                event_type="SHARED_EXPERIENCE"
            )
            self.db.add(timeline_ev)
            await self.db.commit()

        return SharedExperience(
            id=model.id,
            user_id=model.user_id,
            companion_id=model.companion_id,
            title=model.title,
            summary=model.summary,
            started_at=model.started_at,
            last_referenced_at=model.last_referenced_at,
            companion_involvement_level=model.companion_involvement_level,
            is_co_experienced=model.is_co_experienced,
            importance=model.importance
        )

    async def get_story_chapters(
        self,
        user_id: str = "default_user",
        companion_id: str = "default_companion"
    ) -> List[StoryChapter]:
        stmt = (
            select(StoryChapterModel)
            .where(
                StoryChapterModel.user_id == user_id,
                StoryChapterModel.companion_id == companion_id
            )
            .order_by(StoryChapterModel.chapter_number)
        )
        res = await self.db.execute(stmt)
        models = res.scalars().all()

        if not models:
            # Seed Default Genesis Chapters
            ch1 = StoryChapterModel(
                user_id=user_id,
                companion_id=companion_id,
                chapter_number=1,
                title="첫 만남의 설렘",
                theme="BEGINNING",
                summary="처음 대화를 시작하고 서로에 대해 알아가기 시작한 시간.",
                importance=0.9
            )
            ch2 = StoryChapterModel(
                user_id=user_id,
                companion_id=companion_id,
                chapter_number=2,
                title="함께 만든 프로젝트와 성장",
                theme="SHARED_PROJECT",
                summary="AI Companion과 다양한 아이디어를 나누고 실현해 나아가는 과정.",
                importance=0.88
            )
            self.db.add_all([ch1, ch2])
            await self.db.commit()
            models = [ch1, ch2]

        return [
            StoryChapter(
                id=m.id,
                user_id=m.user_id,
                companion_id=m.companion_id,
                chapter_number=m.chapter_number,
                title=m.title,
                theme=m.theme,
                started_at=m.started_at,
                ended_at=m.ended_at,
                summary=m.summary,
                importance=m.importance
            )
            for m in models
        ]

    async def get_timeline(
        self,
        user_id: str = "default_user",
        companion_id: str = "default_companion",
        limit: int = 20
    ) -> List[TimelineEvent]:
        stmt = (
            select(TimelineEventModel)
            .where(
                TimelineEventModel.user_id == user_id,
                TimelineEventModel.companion_id == companion_id
            )
            .order_by(desc(TimelineEventModel.occurred_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        models = res.scalars().all()

        return [
            TimelineEvent(
                id=m.id,
                user_id=m.user_id,
                companion_id=m.companion_id,
                occurred_at=m.occurred_at,
                title=m.title,
                summary=m.summary,
                importance=m.importance,
                event_type=m.event_type
            )
            for m in models
        ]
