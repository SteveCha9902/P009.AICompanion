from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.services.vision_service import VisionService
from app.services.providers.factory import ProviderFactory

router = APIRouter(prefix="/vision", tags=["Vision & Camera Engine"])

def get_vision_service(db: AsyncSession = Depends(get_db)) -> VisionService:
    provider = ProviderFactory.get_vision_provider()
    return VisionService(db=db, provider=provider)

class VisionSessionCreate(BaseModel):
    companion_id: str

class VisionSessionResponse(BaseModel):
    session_id: str
    status: str

@router.post("/sessions", response_model=VisionSessionResponse)
async def create_vision_session(
    request: VisionSessionCreate,
    vision_service: VisionService = Depends(get_vision_service)
):
    try:
        session = vision_service.start_session(companion_id=request.companion_id)
        return VisionSessionResponse(session_id=session.id, status=session.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/observations")
async def process_vision_frame(
    session_id: str,
    file: UploadFile = File(...),
    vision_service: VisionService = Depends(get_vision_service)
):
    """
    Receives a sampled frame from client, analyzes it via VisionProvider,
    applies deduplication, and returns observation.
    """
    try:
        image_data = await file.read()
        observation = await vision_service.process_frame(session_id, image_data)
        
        # Sprint 48 Awareness Processing (Zero Raw Frame Storage, In-Memory DTO)
        from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator
        awareness_ctx = AwarenessEngineCoordinator.process_vision_observation(observation.data)

        return {
            "id": observation.id,
            "observation_type": observation.observation_type,
            "confidence": observation.confidence,
            "data": observation.data,
            "awareness": {
                "user_presence": awareness_ctx.user_state.user_presence,
                "face_detected": awareness_ctx.user_state.face_detected,
                "facial_emotion": awareness_ctx.user_state.facial_emotion.value,
                "attention_level": awareness_ctx.user_state.attention_level,
                "focus_target": awareness_ctx.focus_target.value,
                "detected_objects": [
                    {"type": o.type.value, "confidence": o.confidence, "label": o.label}
                    for o in awareness_ctx.environment_state.detected_objects
                ],
                "awareness_timestamp_ms": awareness_ctx.awareness_timestamp_ms,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/end")
async def end_vision_session(
    session_id: str,
    vision_service: VisionService = Depends(get_vision_service)
):
    try:
        vision_service.end_session(session_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
