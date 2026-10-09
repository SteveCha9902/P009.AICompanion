from typing import Dict, Any
from app.domain.awareness.awareness_context import UserAwarenessState, FacialEmotionType

class UserAwarenessEngine:
    """
    Extracts and quantifies user presence, face detection, gaze, attention, and 8-tier facial emotion.
    """

    EMOTION_MAPPING = {
        "smiling": FacialEmotionType.SMILING,
        "smile": FacialEmotionType.SMILING,
        "happy": FacialEmotionType.SMILING,
        "neutral": FacialEmotionType.NEUTRAL,
        "focused": FacialEmotionType.FOCUSED,
        "focus": FacialEmotionType.FOCUSED,
        "confused": FacialEmotionType.CONFUSED,
        "thinking": FacialEmotionType.THINKING,
        "fatigued": FacialEmotionType.FATIGUED,
        "tired": FacialEmotionType.FATIGUED,
        "surprised": FacialEmotionType.SURPRISED,
        "unknown": FacialEmotionType.UNKNOWN,
    }

    @classmethod
    def analyze_user_presence(cls, raw_vision_data: Dict[str, Any]) -> UserAwarenessState:
        """
        Parses raw structured vision analyzer output into validated UserAwarenessState.
        """
        face_detected = bool(raw_vision_data.get("face_detected", False) or raw_vision_data.get("user_visible", False))
        user_presence = bool(raw_vision_data.get("user_visible", face_detected))
        
        # Gaze direction
        gaze = raw_vision_data.get("gaze", "toward_camera")
        
        # Attention level calculation based on gaze & presence
        base_attention = float(raw_vision_data.get("attention_level", 0.7 if gaze == "toward_camera" else 0.3))
        attention_level = max(0.0, min(1.0, base_attention if face_detected else 0.0))

        # Facial Emotion classification (8-Tier)
        raw_emotion_str = str(raw_vision_data.get("expression", raw_vision_data.get("facial_emotion", "neutral"))).lower()
        facial_emotion = cls.EMOTION_MAPPING.get(raw_emotion_str, FacialEmotionType.UNKNOWN)
        emotion_conf = float(raw_vision_data.get("emotion_confidence", raw_vision_data.get("confidence", 0.85)))

        user_appearance = str(raw_vision_data.get("user_appearance", ""))
        clothing = str(raw_vision_data.get("clothing", ""))

        return UserAwarenessState(
            user_presence=user_presence,
            face_detected=face_detected,
            gaze_direction=gaze,
            attention_level=round(attention_level, 2),
            facial_emotion=facial_emotion,
            emotion_confidence=round(emotion_conf, 2),
            user_appearance=user_appearance,
            clothing=clothing
        )
