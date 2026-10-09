from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, List, Any

from app.db.session import get_db
from app.services.persona_service import PersonaService

router = APIRouter()

class PersonaUpdateRequest(BaseModel):
    name: str = None
    personality: Dict[str, int] = None
    communication_style: Dict[str, str] = None
    values: Dict[str, Any] = None
    behavior_rules: List[str] = None
    boundaries: List[str] = None

@router.get("/personas/me")
async def get_my_persona(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    service = PersonaService(db)
    persona = await service.get_or_create_persona(x_user_id)
    return {
        "id": persona.id,
        "name": persona.name,
        "personality": persona.personality,
        "communication_style": persona.communication_style,
        "values": persona.values,
        "behavior_rules": persona.behavior_rules,
        "boundaries": persona.boundaries,
        "version": persona.version
    }

@router.put("/personas/me")
async def update_my_persona(
    update_data: PersonaUpdateRequest,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    service = PersonaService(db)
    updates = update_data.model_dump(exclude_unset=True)
    persona = await service.update_persona(x_user_id, updates)
    return {"status": "success", "version": persona.version}

@router.post("/personas/me/preset/{preset_name}")
async def apply_preset(
    preset_name: str,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    service = PersonaService(db)
    try:
        persona = await service.apply_preset(x_user_id, preset_name)
        return {"status": "success", "version": persona.version}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
