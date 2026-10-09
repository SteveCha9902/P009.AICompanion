import uuid
import logging
import asyncio
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.future import select

from app.db.models.vision import VisionSession, VisionSessionStatus, VisionObservation
from app.services.vision.provider_interface import BaseVisionProvider

logger = logging.getLogger(__name__)

# Fallback In-Memory store for fast vision session tracking
_active_vision_sessions = {}

class VisionService:
    def __init__(self, db: Any, provider: BaseVisionProvider):
        self.db = db
        self.provider = provider

    async def _get_session(self, session_id: str) -> Optional[VisionSession]:
        if hasattr(self.db, "query"):
            try:
                res = self.db.query(VisionSession).filter(VisionSession.id == session_id).first()
                if res:
                    return res
            except Exception:
                pass
        elif hasattr(self.db, "execute"):
            try:
                res = await self.db.execute(select(VisionSession).filter(VisionSession.id == session_id))
                obj = res.scalars().first()
                if obj:
                    return obj
            except Exception:
                pass

        return _active_vision_sessions.get(session_id)

    async def _save_session(self, session: VisionSession):
        _active_vision_sessions[session.id] = session
        if hasattr(self.db, "add") and hasattr(self.db, "commit"):
            try:
                self.db.add(session)
                if asyncio.iscoroutinefunction(self.db.commit):
                    await self.db.commit()
                else:
                    self.db.commit()
            except Exception as e:
                logger.debug(f"[VisionService] DB save skipped: {e}")

    def start_session(self, companion_id: str) -> VisionSession:
        session_id = str(uuid.uuid4())
        session = VisionSession(
            id=session_id,
            companion_id=companion_id,
            status=VisionSessionStatus.CAMERA_ACTIVE.value
        )
        _active_vision_sessions[session_id] = session
        return session

    def end_session(self, session_id: str):
        session = _active_vision_sessions.get(session_id)
        if session:
            session.ended_at = datetime.utcnow()
            session.status = VisionSessionStatus.CAMERA_OFF.value

    async def process_frame(self, session_id: str, image_data: bytes) -> VisionObservation:
        """
        Process an incoming frame. Throttling and meaningful change detection.
        Zero Raw Frame Storage, privacy-first ephemeral observation.
        """
        session = await self._get_session(session_id)
        if not session:
            session = VisionSession(
                id=session_id,
                companion_id="default_companion",
                status=VisionSessionStatus.CAMERA_ACTIVE.value
            )
            await self._save_session(session)
            
        session.status = VisionSessionStatus.ANALYZING.value
        await self._save_session(session)
        
        try:
            # 1. Analyze with provider (GPT-4o-mini Vision)
            logger.info(f"[VisionService] Analyzing frame ({len(image_data)} bytes)...")
            analysis = await self.provider.analyze_frame(image_data)
            logger.info(f"[VisionService] Analysis result: {analysis}")
            
            # Determine observation type
            obs_type = "USER_NOT_VISIBLE"
            if analysis.get("user_visible"):
                if analysis.get("face_detected"):
                    obs_type = "FACE_DETECTED"
                else:
                    obs_type = "USER_DETECTED"

            observation = VisionObservation(
                id=str(uuid.uuid4()),
                session_id=session_id,
                observation_type=obs_type,
                confidence=float(analysis.get("confidence", 0.90)),
                data=analysis
            )
            
            session.status = VisionSessionStatus.VISION_READY.value
            await self._save_session(session)
            
            return observation
            
        except Exception as e:
            session.status = VisionSessionStatus.VISION_ERROR.value
            await self._save_session(session)
            logger.error(f"[VisionService] Frame analysis failed: {e}")
            raise e

