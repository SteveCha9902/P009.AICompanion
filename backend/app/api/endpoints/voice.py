import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import Response

logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.services.voice_service import VoiceService
from app.services.providers.factory import ProviderFactory
from app.services.companion.runtime import create_companion_orchestrator

router = APIRouter(prefix="/voice", tags=["Voice Interaction Engine"])

class VoiceSessionCreate(BaseModel):
    user_id: str
    companion_id: str
    conversation_id: str

class VoiceSessionResponse(BaseModel):
    session_id: str
    status: str

async def get_voice_service(
    x_user_id: Optional[str] = Header(default="default_user"),
    db: AsyncSession = Depends(get_db)
) -> VoiceService:
    orchestrator = await create_companion_orchestrator(db=db, user_id=x_user_id)
    stt_provider = ProviderFactory.get_stt_provider()
    tts_provider = ProviderFactory.get_tts_provider()
    return VoiceService(
        db=db,
        stt_provider=stt_provider,
        tts_provider=tts_provider,
        orchestrator=orchestrator
    )

@router.post("/sessions", response_model=VoiceSessionResponse)
async def create_voice_session(
    request: VoiceSessionCreate,
    voice_service: VoiceService = Depends(get_voice_service)
):
    try:
        session = voice_service.create_session(
            user_id=request.user_id,
            companion_id=request.companion_id,
            conversation_id=request.conversation_id
        )
        return VoiceSessionResponse(session_id=session.session_id, status=session.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AudioBase64Request(BaseModel):
    audio_base64: str
    user_id: Optional[str] = "default_user"
    companion_id: Optional[str] = "default_companion"
    conversation_id: Optional[str] = "default"

@router.post("/sessions/{session_id}/audio-base64")
async def process_voice_audio_base64(
    session_id: str,
    body: AudioBase64Request,
    voice_service: VoiceService = Depends(get_voice_service)
):
    try:
        import base64
        audio_data = base64.b64decode(body.audio_base64)
        logger.info(f"[VoiceAPI] Received Base64 audio upload: {len(audio_data)} bytes decoded for session {session_id}, companion={body.companion_id}")
        audio_response, transcript, response_text = await voice_service.process_audio(
            session_id=session_id,
            audio_data=audio_data,
            user_id=body.user_id,
            companion_id=body.companion_id,
            conversation_id=body.conversation_id
        )
        
        audio_b64 = base64.b64encode(audio_response).decode('utf-8') if audio_response else ""
        
        return {
            "status": "success",
            "session_id": session_id,
            "transcript": transcript or "",
            "response_text": response_text or "",
            "audio_base64": audio_b64
        }
    except Exception as e:
        logger.error(f"[VoiceAPI] Base64 audio processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/audio")
async def process_voice_audio(
    session_id: str,
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(default="default_user"),
    companion_id: Optional[str] = Form(default="default_companion"),
    conversation_id: Optional[str] = Form(default="default"),
    image_base64: Optional[str] = Form(default=None),
    camera_timestamp_ms: Optional[int] = Form(default=None),
    voice_service: VoiceService = Depends(get_voice_service)
):
    try:
        import base64
        audio_data = await file.read()
        image_data = None
        if image_base64 and len(image_base64) > 100:
            try:
                # Strip potential data URL prefix
                raw_b64 = image_base64.split(",")[-1]
                image_data = base64.b64decode(raw_b64)
                logger.info(f"[VoiceAPI] One-Shot Multimodal: Bound camera frame ({len(image_data)} bytes, ts={camera_timestamp_ms}) with voice")
            except Exception as img_err:
                logger.warning(f"[VoiceAPI] Failed to decode bound camera frame (Fallback to Audio-only): {img_err}")

        logger.info(f"[VoiceAPI] Received audio upload: filename={file.filename}, size={len(audio_data)} bytes, companion={companion_id}")
        audio_response, transcript, response_text = await voice_service.process_audio(
            session_id=session_id,
            audio_data=audio_data,
            user_id=user_id,
            companion_id=companion_id,
            conversation_id=conversation_id,
            image_data=image_data,
            camera_timestamp_ms=camera_timestamp_ms,
        )
        
        audio_b64 = base64.b64encode(audio_response).decode('utf-8') if audio_response else ""

        
        return {
            "status": "success",
            "session_id": session_id,
            "transcript": transcript or "",
            "response_text": response_text or "",
            "audio_base64": audio_b64
        }
    except ValueError as e:
        logger.error(f"[VoiceAPI] ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[VoiceAPI] Server error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/interrupt")
async def interrupt_voice_session(
    session_id: str,
    voice_service: VoiceService = Depends(get_voice_service)
):
    try:
        voice_service.interrupt_session(session_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/end")
async def end_voice_session(
    session_id: str,
    voice_service: VoiceService = Depends(get_voice_service)
):
    try:
        voice_service.end_session(session_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.services.voice_realtime_channel import VoiceRealtimeSessionHandler
from app.db.session import async_session

@router.websocket("/live-ws")
async def voice_realtime_websocket(websocket: WebSocket):
    async with async_session() as db:
        orchestrator = await create_companion_orchestrator(db=db, user_id="default_user")
        stt_provider = ProviderFactory.get_stt_provider()
        tts_provider = ProviderFactory.get_tts_provider()
        handler = VoiceRealtimeSessionHandler(
            websocket=websocket,
            stt_provider=stt_provider,
            tts_provider=tts_provider,
            orchestrator=orchestrator,
            db=db
        )
        await handler.run()

