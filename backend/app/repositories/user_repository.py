from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_external_id(self, external_id: string) -> User | None:
        result = await self.session.execute(select(User).where(User.external_id == external_id))
        return result.scalars().first()

    async def create(self, external_id: str) -> User:
        user = User(external_id=external_id)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
