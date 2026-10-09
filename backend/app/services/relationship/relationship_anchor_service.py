import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.models.relationship import RelationshipAnchorModel
from app.domain.relationship.relationship_anchor import RelationshipAnchor, RelationshipAnchorType

logger = logging.getLogger(__name__)

class RelationshipAnchorService:
    """
    Manages immutable relational anchors and historical milestone timeline.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_anchor(
        self,
        user_id: str,
        companion_id: str,
        anchor_type: RelationshipAnchorType,
        summary: str,
        importance: float = 0.8
    ) -> RelationshipAnchor:
        model = RelationshipAnchorModel(
            user_id=user_id,
            companion_id=companion_id,
            anchor_type=anchor_type.value,
            summary=summary,
            importance=importance
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)

        return RelationshipAnchor(
            id=model.id,
            user_id=model.user_id,
            companion_id=model.companion_id,
            anchor_type=anchor_type,
            summary=model.summary,
            importance=model.importance,
            created_at=model.created_at
        )

    async def get_anchors(
        self,
        user_id: str,
        companion_id: str,
        limit: int = 10
    ) -> List[RelationshipAnchor]:
        stmt = (
            select(RelationshipAnchorModel)
            .where(
                RelationshipAnchorModel.user_id == user_id,
                RelationshipAnchorModel.companion_id == companion_id
            )
            .order_by(desc(RelationshipAnchorModel.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        models = res.scalars().all()

        return [
            RelationshipAnchor(
                id=m.id,
                user_id=m.user_id,
                companion_id=m.companion_id,
                anchor_type=RelationshipAnchorType(m.anchor_type),
                summary=m.summary,
                importance=m.importance,
                created_at=m.created_at
            )
            for m in models
        ]
