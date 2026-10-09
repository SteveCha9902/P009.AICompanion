from typing import List, Optional, Dict, Any
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    ExpressionParameters,
    FaceParameters,
    SpeechParameters,
    BehaviorParameters,
    RelationshipParameters,
    MotionParameters,
    AvatarMotion,
    VisemeType,
    AvatarGesture,
    AvatarBehaviorPlan
)
from app.services.character.avatar.expression_mapper import EmotionToExpressionMapper
from app.services.character.avatar.baseline_controller import AvatarBaselineController
from app.services.character.avatar.variety_engine import MotionVarietyEngine
from app.services.character.domain import CharacterDecision, BehaviorIntent

class AvatarBehaviorController:
    """
    Coordinates real-time cognitive state, event-driven 6-state transitions,
    multi-gesture compositions, Face/Speech/Behavior parameters, Relationship modifiers,
    and Behavioral Variety Engine (Sprint 45).
    """

    @classmethod
    def evaluate_plan(
        cls,
        state: AvatarBehavioralState,
        decision: Optional[CharacterDecision] = None,
        custom_emotion: Optional[ContinuousEmotionVector] = None,
        custom_relationship: Optional[RelationshipParameters] = None,
        active_gestures: Optional[List[AvatarGesture]] = None,
        thinking_elapsed_sec: float = 0.0
    ) -> AvatarBehaviorPlan:
        # 1. Resolve Emotion Vector
        if custom_emotion:
            emo = custom_emotion
        elif decision:
            if decision.response_style.value in ["cheerful_energetic", "playful_teasing"]:
                emo = ContinuousEmotionVector(valence=0.8, arousal=0.7, warmth=0.85, intensity=0.8)
            elif decision.response_style.value in ["warm_supportive", "gentle_listening"]:
                emo = ContinuousEmotionVector(valence=0.5, arousal=0.4, warmth=0.9, intensity=0.6)
            elif decision.response_style.value in ["calm_reflective", "serious_advisory"]:
                emo = ContinuousEmotionVector(valence=0.1, arousal=0.3, warmth=0.6, intensity=0.5)
            else:
                emo = ContinuousEmotionVector(valence=0.3, arousal=0.5, warmth=0.7, intensity=0.5)
        else:
            emo = ContinuousEmotionVector(valence=0.2, arousal=0.4, warmth=0.6, intensity=0.3)

        # 2. Derive Relationship Parameters
        relationship = custom_relationship or RelationshipParameters()

        # 3. Derive Expression Parameters with Relationship Bias
        expr = EmotionToExpressionMapper.map_emotion_to_expression(emo, relationship=relationship)

        # 4. Select Motion from Variety Engine
        selected_motion = MotionVarietyEngine.select_motion(
            state=state,
            decision=decision,
            emotion=emo,
            relationship=relationship
        )
        motion_params = MotionVarietyEngine.generate_motion_parameters(selected_motion)

        # 5. Handle 6-Stage Behavioral States & Parameters
        gestures: List[AvatarGesture] = list(active_gestures) if active_gestures else []
        attention = 0.8
        transition_ms = 300
        speech_sync_ready = False

        # Base FaceParameters
        face = FaceParameters(
            eye_openness=expr.eye_openness,
            blink_weight=0.0,
            eye_direction_x=0.0,
            eye_direction_y=0.0,
            mouth_open=0.0,
            smile_strength=expr.smile_strength,
            brow_raise=expr.brow_raise,
            head_pitch=expr.head_pitch + motion_params.head_pitch,
            head_yaw=expr.head_yaw + motion_params.head_yaw,
            head_roll=expr.head_roll,
            warmth=expr.warmth_alpha
        )

        # Base SpeechParameters
        speech = SpeechParameters(
            is_speaking=False,
            mouth_open=0.0,
            viseme=VisemeType.CLOSED,
            speech_intensity=0.5,
            speech_progress=0.0
        )

        # Base BehaviorParameters
        base_eye_contact = round(min(1.0, max(0.0, 0.8 + 0.2 * relationship.trust + selected_motion.eye_contact_bias)), 2)
        behavior = BehaviorParameters(
            attention_level=0.8,
            eye_contact=base_eye_contact,
            head_tilt=round(motion_params.head_tilt, 2),
            nod_intensity=round(motion_params.nod_intensity, 2),
            body_lean=round(relationship.warmth * 0.4 + motion_params.body_lean, 2),
            curiosity_level=0.5,
            thinking_intensity=0.0
        )

        if state == AvatarBehavioralState.IDLE:
            attention = 0.6
            transition_ms = 500
            face.eye_openness = 0.85
            face.smile_strength = min(1.0, 0.20 + 0.15 * relationship.familiarity)
            behavior.attention_level = 0.65

        elif state == AvatarBehavioralState.LISTENING:
            attention = 0.95
            transition_ms = 250
            expr.brow_raise = 0.2
            face.eye_openness = 1.0
            face.brow_raise = 0.35
            behavior.attention_level = 0.95
            behavior.eye_contact = 1.0
            behavior.curiosity_level = 0.85
            behavior.nod_intensity = round(max(0.6, motion_params.nod_intensity), 2)
            behavior.head_tilt = round(max(2.5, motion_params.head_tilt), 2)
            if not any(g.gesture_type == "SUBTLE_NOD" for g in gestures):
                gestures.append(AvatarGesture(gesture_type="SUBTLE_NOD", intensity=0.6))


        elif state == AvatarBehavioralState.THINKING:
            attention = 0.7
            expr.head_roll = 4.0 + min(4.0, thinking_elapsed_sec * 0.8)
            expr.eye_softness = 0.6
            face.eye_openness = 0.8
            face.eye_direction_y = -0.4
            face.head_roll = -4.0
            face.head_pitch = -2.0
            face.smile_strength = 0.15
            behavior.attention_level = 0.70
            behavior.eye_contact = 0.40
            behavior.head_tilt = round(min(-2.5, motion_params.head_tilt), 2)
            behavior.thinking_intensity = 0.85
            if not any(g.gesture_type == "THINKING_TILT" for g in gestures):
                gestures.append(AvatarGesture(gesture_type="THINKING_TILT", intensity=0.8))

        elif state == AvatarBehavioralState.PRE_EXPRESSION:
            attention = 0.9
            transition_ms = 200
            speech_sync_ready = True
            face.smile_strength = min(1.0, 0.75 + 0.15 * relationship.familiarity)
            face.eye_openness = 0.95
            behavior.attention_level = 0.90
            behavior.eye_contact = 0.90

        elif state == AvatarBehavioralState.SPEAKING:
            attention = 0.9
            speech_sync_ready = True
            transition_ms = 150
            face.mouth_open = 0.55
            face.smile_strength = max(0.5, expr.smile_strength)
            speech.is_speaking = True
            speech.mouth_open = 0.55
            speech.viseme = VisemeType.A
            speech.speech_intensity = 0.7
            speech.speech_progress = 0.5
            behavior.attention_level = 0.90
            if decision and BehaviorIntent.CELEBRATE_SUCCESS in decision.behavior_intents:
                if not any(g.gesture_type == "CHEERFUL_WAVE" for g in gestures):
                    gestures.append(AvatarGesture(gesture_type="CHEERFUL_WAVE", intensity=0.7))
            elif decision and BehaviorIntent.COMFORT_USER in decision.behavior_intents:
                if not any(g.gesture_type == "WARM_LEAN" for g in gestures):
                    gestures.append(AvatarGesture(gesture_type="WARM_LEAN", intensity=0.6))

        elif state == AvatarBehavioralState.SETTLING:
            attention = 0.75
            transition_ms = 400
            face.mouth_open = 0.0
            face.smile_strength = 0.35
            speech.is_speaking = False
            speech.mouth_open = 0.0
            speech.viseme = VisemeType.CLOSED
            behavior.attention_level = 0.75
            behavior.eye_contact = 0.85
            behavior.head_tilt = 0.5

        # 6. Baseline Motion Parameters
        baseline = AvatarBaselineController.get_baseline_parameters()

        return AvatarBehaviorPlan(
            state=state,
            expression=expr,
            face_parameters=face,
            speech_parameters=speech,
            behavior_parameters=behavior,
            relationship_parameters=relationship,
            motion_parameters=motion_params,
            selected_motion=selected_motion,
            active_gestures=gestures,
            attention_level=attention,
            transition_duration_ms=transition_ms,
            speech_sync_ready=speech_sync_ready,
            metadata={"baseline": baseline}
        )
