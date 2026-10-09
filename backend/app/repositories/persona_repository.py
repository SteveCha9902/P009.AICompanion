from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.persona import Persona

class PersonaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, companion_id: str, **kwargs) -> Persona:
        persona = Persona(companion_id=companion_id, **kwargs)
        self.session.add(persona)
        await self.session.commit()
        await self.session.refresh(persona)
        return persona

    async def get_by_companion_id(self, companion_id: str) -> Optional[Persona]:
        result = await self.session.execute(
            select(Persona).where(Persona.companion_id == companion_id)
        )
        return result.scalars().first()

    async def update(self, persona: Persona, **kwargs) -> Persona:
        for key, value in kwargs.items():
            if hasattr(persona, key):
                setattr(persona, key, value)
        
        persona.version += 1
        self.session.add(persona)
        await self.session.commit()
        await self.session.refresh(persona)
        return persona
