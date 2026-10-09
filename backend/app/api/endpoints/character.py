from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.services.character.character_service import CharacterService
from app.services.character.character_state_resolver import CharacterStateResolver
from app.services.character.response_strategy_resolver import ResponseStrategyResolver

router = APIRouter(prefix="/character", tags=["Character Identity & Personality Core"])

class StrategyRequest(BaseModel):
    user_input: str

@router.get("/profile")
async def get_character_profile(
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns full persistent Character DNA (Identity, Multi-dimensional Personality, Values, Preferences, Boundaries).
    """
    try:
        service = CharacterService(db)
        char_data = await service.get_or_create_character(companion_id=companion_id)
        return {
            "identity": char_data["identity"].model_dump(),
            "personality": char_data["personality"].model_dump(),
            "values": char_data["values"].model_dump(),
            "preferences": [p.model_dump() for p in char_data["preferences"]],
            "boundaries": [b.model_dump() for b in char_data["boundaries"]],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state")
async def get_character_state(
    companion_id: str = Query(default="default_companion"),
    current_mood: str = Query(default="neutral"),
    relationship_level: str = Query(default="FRIEND"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns the real-time situational Character State modulated by mood and relationship.
    """
    try:
        service = CharacterService(db)
        char_data = await service.get_or_create_character(companion_id=companion_id)
        state = CharacterStateResolver.resolve(
            companion_id=companion_id,
            personality=char_data["personality"],
            current_mood=current_mood,
            relationship_level=relationship_level
        )
        return state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agency/evaluate")
async def evaluate_character_agency(
    req: StrategyRequest,
    companion_id: str = Query(default="default_companion"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Evaluates user input against Character Values and Boundaries to output ResponseStrategy.
    """
    try:
        service = CharacterService(db)
        char_data = await service.get_or_create_character(companion_id=companion_id)
        strategy = ResponseStrategyResolver.resolve_strategy(
            user_input=req.user_input,
            values=char_data["values"],
            boundaries=char_data["boundaries"]
        )
        return strategy.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
