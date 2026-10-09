from typing import Dict, List
from app.services.character.avatar.domain import AvatarMotion

class MotionLibrary:
    """
    Standard Motion Library V1 (Sprint 45).
    Catalog of 12 distinct physical motion primitives across Listening, Thinking, Speaking, and Empathy.
    """

    MOTIONS: Dict[str, AvatarMotion] = {
        # 1. Listening Motions (4)
        "LISTENING_SOFT_NOD": AvatarMotion(
            motion_id="LISTENING_SOFT_NOD",
            category="listening",
            head_pitch_delta=1.5,
            nod_intensity_delta=0.4,
            duration_ms=1200
        ),
        "LISTENING_DEEP_NOD": AvatarMotion(
            motion_id="LISTENING_DEEP_NOD",
            category="listening",
            head_pitch_delta=3.0,
            nod_intensity_delta=0.8,
            duration_ms=1500
        ),
        "LISTENING_SIDE_TILT": AvatarMotion(
            motion_id="LISTENING_SIDE_TILT",
            category="listening",
            head_tilt_delta=3.0,
            eye_contact_bias=0.1,
            duration_ms=1800
        ),
        "LISTENING_FOCUS_LEAN": AvatarMotion(
            motion_id="LISTENING_FOCUS_LEAN",
            category="listening",
            body_lean_delta=0.4,
            eye_contact_bias=0.15,
            duration_ms=2000
        ),

        # 2. Thinking Motions (4)
        "THINKING_TILT": AvatarMotion(
            motion_id="THINKING_TILT",
            category="thinking",
            head_tilt_delta=-4.0,
            head_pitch_delta=-2.0,
            duration_ms=2200
        ),
        "THINKING_DOWN_GAZE": AvatarMotion(
            motion_id="THINKING_DOWN_GAZE",
            category="thinking",
            head_pitch_delta=-3.0,
            eye_contact_bias=-0.4,
            duration_ms=2000
        ),
        "THINKING_SIDE_GAZE": AvatarMotion(
            motion_id="THINKING_SIDE_GAZE",
            category="thinking",
            head_yaw_delta=2.5,
            eye_contact_bias=-0.3,
            duration_ms=1900
        ),
        "THINKING_REFLECTION": AvatarMotion(
            motion_id="THINKING_REFLECTION",
            category="thinking",
            head_tilt_delta=-2.5,
            eye_contact_bias=-0.2,
            duration_ms=2500
        ),

        # 3. Speaking Motions (3)
        "SPEAKING_GENTLE_EMPHASIS": AvatarMotion(
            motion_id="SPEAKING_GENTLE_EMPHASIS",
            category="speaking",
            head_pitch_delta=1.2,
            nod_intensity_delta=0.3,
            smile_delta=0.1,
            duration_ms=1400
        ),
        "SPEAKING_WARM_LEAN": AvatarMotion(
            motion_id="SPEAKING_WARM_LEAN",
            category="speaking",
            body_lean_delta=0.3,
            smile_delta=0.15,
            duration_ms=1600
        ),
        "SPEAKING_SMALL_HEAD_TURN": AvatarMotion(
            motion_id="SPEAKING_SMALL_HEAD_TURN",
            category="speaking",
            head_yaw_delta=2.0,
            smile_delta=0.2,
            duration_ms=1500
        ),

        # 4. Empathy Motions (3)
        "EMPATHY_SOFT_NOD": AvatarMotion(
            motion_id="EMPATHY_SOFT_NOD",
            category="empathy",
            nod_intensity_delta=0.5,
            head_pitch_delta=1.0,
            duration_ms=1600
        ),
        "EMPATHY_CONCERN_TILT": AvatarMotion(
            motion_id="EMPATHY_CONCERN_TILT",
            category="empathy",
            head_tilt_delta=2.0,
            eye_contact_bias=0.1,
            duration_ms=1800
        ),
        "EMPATHY_SUPPORTIVE_LEAN": AvatarMotion(
            motion_id="EMPATHY_SUPPORTIVE_LEAN",
            category="empathy",
            body_lean_delta=0.5,
            eye_contact_bias=0.15,
            duration_ms=2000
        )
    }

    @classmethod
    def get_motions_by_category(cls, category: str) -> List[AvatarMotion]:
        return [m for m in cls.MOTIONS.values() if m.category == category]
