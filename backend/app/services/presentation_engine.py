from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models.emotion import EmotionState
from app.db.models.relationship import RelationshipState
from app.db.models.presence import PresenceState
from app.db.models.voice_session import VoiceSession, VoiceSessionStatus
from app.db.models.vision import VisionSession, VisionObservation

import datetime

class AvatarStateResolver:
    def __init__(self, db: Session):
        self.db = db
        self.state_version = 0

    def resolve(self, companion_id: str) -> Dict[str, Any]:
        """
        Calculates the semantic Avatar State based on Cognitive Core states.
        Does NOT handle real-time rendering logic like audio sync.
        """
        self.state_version += 1

        # 1. Fetch current states safely
        emotion = None
        relationship = None
        presence = None
        voice_session = None
        vision_session = None

        if self.db is not None and hasattr(self.db, "query"):
            try:
                emotion = self.db.query(EmotionState).filter(EmotionState.companion_id == companion_id).first()
                relationship = self.db.query(RelationshipState).filter(RelationshipState.companion_id == companion_id).first()
                presence = self.db.query(PresenceState).filter(PresenceState.companion_id == companion_id).first()
                voice_session = self.db.query(VoiceSession).filter(VoiceSession.companion_id == companion_id).order_by(VoiceSession.started_at.desc()).first()
                vision_session = self.db.query(VisionSession).filter(VisionSession.companion_id == companion_id).order_by(VisionSession.started_at.desc()).first()
            except Exception:
                pass
        
        # Default Semantic State

        avatar_state = {
            "state_version": self.state_version,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "expression": "neutral",
            "animation": "idle",
            "gaze": "user",
            "speaking": False,
            "listening": False,
            "intensity": 0.5,
            "energy": 0.5
        }

        # 2. Presence Evaluation (Base Activity Level)
        if presence:
            if presence.state == "OFFLINE":
                avatar_state["animation"] = "hidden"
                return avatar_state
            elif presence.state == "AWAY":
                avatar_state["animation"] = "reduced"
            elif presence.state == "SLEEPING":
                avatar_state["expression"] = "sleeping"
                avatar_state["animation"] = "breathing"
                avatar_state["gaze"] = "closed"
                return avatar_state # Sleeping overrides most things

        # 3. Voice State Evaluation (Semantic)
        if voice_session and voice_session.status != VoiceSessionStatus.IDLE.value:
            if voice_session.status == VoiceSessionStatus.LISTENING.value:
                avatar_state["listening"] = True
                avatar_state["animation"] = "attentive"
            elif voice_session.status == VoiceSessionStatus.THINKING.value:
                avatar_state["animation"] = "thinking"
                avatar_state["gaze"] = "away" # Looking up/away while thinking
            elif voice_session.status == VoiceSessionStatus.SPEAKING.value:
                # Semantic speaking intention (Real-time is controlled by Mobile)
                avatar_state["animation"] = "speaking"

            
        # 4. Emotion & Relationship -> Expression Mapping
        if emotion:
            intensity_mod = 1.0
            
            # Relationship modifies intensity/style
            if relationship:
                if relationship.current_stage == "STRANGER":
                    intensity_mod = 0.5
                    avatar_state["animation"] = "restrained"
                elif relationship.current_stage == "CLOSE":
                    intensity_mod = 1.2
                    if avatar_state["animation"] == "idle":
                        avatar_state["animation"] = "relaxed"
            
            # Emotion to Expression Policy
            primary_emotion = emotion.primary_emotion
            intensity = min(1.0, emotion.intensity * intensity_mod)
            avatar_state["intensity"] = round(intensity, 2)
            
            if primary_emotion == "JOY":
                avatar_state["expression"] = "warm_smile" if intensity > 0.7 else "smile"
            elif primary_emotion == "EMPATHY":
                avatar_state["expression"] = "soft"
            elif primary_emotion == "CURIOSITY":
                avatar_state["expression"] = "curious"
            elif primary_emotion == "SURPRISE":
                avatar_state["expression"] = "surprised"
            elif primary_emotion == "FRUSTRATION":
                avatar_state["expression"] = "restrained"

        # 5. Vision -> Gaze Mapping (Observational influence, not override)
        if vision_session and vision_session.status != "CAMERA_OFF":
            latest_obs = self.db.query(VisionObservation).filter(VisionObservation.session_id == vision_session.id).order_by(VisionObservation.created_at.desc()).first()
            if latest_obs and latest_obs.confidence >= 0.6:
                if latest_obs.observation_type == "USER_NOT_VISIBLE":
                    avatar_state["gaze"] = "searching"
                    avatar_state["animation"] = "reduced"
                elif latest_obs.observation_type == "FACE_DETECTED":
                    # If we see the user's face, try to make eye contact unless we are thinking
                    if avatar_state["animation"] != "thinking":
                        avatar_state["gaze"] = "user"

        return avatar_state
