from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.companion import Companion

class CompanionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, name: str = "Luna") -> Companion:
        companion = Companion(user_id=user_id, name=name)
        self.session.add(companion)
        await self.session.commit()
        await self.session.refresh(companion)
        return companion

    async def get_by_user_id(self, user_id: str) -> Optional[Companion]:
        result = await self.session.execute(
            select(Companion).where(Companion.user_id == user_id)
        )
        return result.scalars().first()
