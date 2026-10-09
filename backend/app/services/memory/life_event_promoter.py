import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.autobiographical_memory import LifeEventModel, EpisodicMemoryModel
from app.domain.memory.life_event import LifeEvent, LifeEventCategory
from app.domain.memory.episodic_memory import EpisodicMemory

logger = logging.getLogger(__name__)

PROMOTION_THRESHOLD = 0.70

class LifeEventPromoter:
    """
    Evaluates Episodic Memories and promotes qualifying high-importance episodes to Life Events
    with strict duplicate detection and validation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_and_promote(
        self,
        episode: EpisodicMemory
    ) -> Optional[LifeEvent]:
        # 1. Importance Threshold Check
        if episode.importance < PROMOTION_THRESHOLD:
            return None

        # 2. Duplicate Detection: Check if a similar Life Event already exists
        stmt = (
            select(LifeEventModel)
            .where(
                LifeEventModel.user_id == episode.user_id,
                LifeEventModel.companion_id == episode.companion_id
            )
        )
        res = await self.db.execute(stmt)
        existing_events = res.scalars().all()

        for ev in existing_events:
            # If summary contains identical core phrase or title matches
            if ev.summary.strip().lower() == episode.summary.strip().lower():
                logger.info(f"[LifeEventPromoter] Duplicate Life Event skipped: '{episode.summary}'")
                return None

        # 3. Categorization
        category = LifeEventCategory.PERSONAL_MILESTONE
        summary_lower = episode.summary.lower()
        if any(kw in summary_lower for kw in ["프로젝트", "개발", "코딩", "project", "code", "prototype"]):
            category = LifeEventCategory.PROJECT_MILESTONE
        elif any(kw in summary_lower for kw in ["이직", "승진", "면접", "취업", "career", "job"]):
            category = LifeEventCategory.CAREER_EVENT
        elif any(kw in summary_lower for kw in ["어려움", "힘든", "고민", "struggle", "difficult"]):
            category = LifeEventCategory.DIFFICULT_PERIOD
        elif any(kw in summary_lower for kw in ["지니", "관계", "우리", "companion", "friendship"]):
            category = LifeEventCategory.RELATIONSHIP_MILESTONE

        title = episode.summary[:30] + "..." if len(episode.summary) > 30 else episode.summary

        # 4. Persist Life Event
        import uuid
        event_id = str(uuid.uuid4())
        model = LifeEventModel(
            id=event_id,
            user_id=episode.user_id,
            companion_id=episode.companion_id,
            title=title,
            summary=episode.summary,
            category=category.value,
            occurred_at=episode.occurred_at,
            importance=episode.importance,
            emotional_weight=round(episode.importance * 0.9, 2),
            relationship_significance=round(episode.importance * 0.85, 2),
            source_episode_ids=[episode.id]
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)

        logger.info(f"[LifeEventPromoter] Promoted episode {episode.id} to Life Event '{title}' ({category.value})")

        return LifeEvent(
            id=model.id or event_id,
            user_id=model.user_id,
            companion_id=model.companion_id,
            title=model.title,
            summary=model.summary,
            category=category,
            occurred_at=model.occurred_at,
            importance=model.importance,
            emotional_weight=model.emotional_weight,
            relationship_significance=model.relationship_significance,
            source_episode_ids=model.source_episode_ids
        )

