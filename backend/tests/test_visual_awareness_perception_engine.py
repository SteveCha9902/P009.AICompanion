import pytest
import time
from app.domain.awareness.awareness_context import (
    AwarenessContext,
    UserAwarenessState,
    EnvironmentAwarenessState,
    FacialEmotionType,
    SceneObjectType,
    VisualFocusTarget,
    DetectedObject,
    BoundingBox
)
from app.services.awareness.user_awareness_engine import UserAwarenessEngine
from app.services.awareness.environment_awareness_engine import EnvironmentAwarenessEngine
from app.services.awareness.reaction_planner import AwarenessReactionPlanner, ReactionBudgetManager
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator
from app.services.context.providers.awareness_provider import AwarenessContextProvider

def test_gate_va1_user_detection_and_8_tier_emotion():
    """
    Gate VA1: User Detection parses presence, gaze, attention, and 8-tier facial emotions accurately.
    """
    raw_vision_data = {
        "face_detected": True,
        "user_visible": True,
        "gaze": "toward_camera",
        "attention_level": 0.95,
        "expression": "focused",
        "emotion_confidence": 0.92
    }
    user_state = UserAwarenessEngine.analyze_user_presence(raw_vision_data)

    assert user_state.user_presence is True
    assert user_state.face_detected is True
    assert user_state.gaze_direction == "toward_camera"
    assert user_state.attention_level == 0.95
    assert user_state.facial_emotion == FacialEmotionType.FOCUSED
    assert user_state.emotion_confidence == 0.92

    # Test Fatigue and Confusion mappings
    fatigue_state = UserAwarenessEngine.analyze_user_presence({"expression": "tired", "face_detected": True})
    assert fatigue_state.facial_emotion == FacialEmotionType.FATIGUED

    confused_state = UserAwarenessEngine.analyze_user_presence({"expression": "confused", "face_detected": True})
    assert confused_state.facial_emotion == FacialEmotionType.CONFUSED


def test_gate_va2_scene_object_detection_and_confidence_threshold():
    """
    Gate VA2: Environment Awareness detects 8 major object types and enforces confidence thresholding.
    """
    raw_env_data = {
        "objects": [
            {"label": "cup", "confidence": 0.92, "bbox": {"x_min": 0.1, "y_min": 0.2, "x_max": 0.3, "y_max": 0.4}},
            {"label": "laptop", "confidence": 0.88},
            {"label": "pet", "confidence": 0.45}, # Low confidence
            {"label": "plant", "confidence": 0.80}
        ],
        "scene_description": "User sitting at desk with coffee",
        "ambient_light": "bright"
    }
    env_state = EnvironmentAwarenessEngine.analyze_environment(raw_env_data)

    assert len(env_state.detected_objects) == 4
    cup_obj = next(o for o in env_state.detected_objects if o.type == SceneObjectType.CUP)
    assert cup_obj.confidence == 0.92
    assert cup_obj.bbox is not None
    assert cup_obj.bbox.x_min == 0.1

    # High-confidence filter test (>= 0.70)
    context = AwarenessContext(environment_state=env_state)
    high_conf = context.get_high_confidence_objects(min_confidence=0.70)
    assert len(high_conf) == 3 # cup, laptop, plant (pet with 0.45 excluded)
    assert not any(o.type == SceneObjectType.PET for o in high_conf)


def test_gate_va3_awareness_freshness_and_staleness_filter():
    """
    Gate VA3: Freshness validation ensures observations older than 10 seconds are flagged and excluded.
    """
    # Fresh context (0s age)
    fresh_context = AwarenessContext(
        awareness_timestamp_ms=int(time.time() * 1000)
    )
    assert fresh_context.is_fresh is True
    assert fresh_context.age_ms < 1000

    # Stale context (15s ago)
    stale_context = AwarenessContext(
        awareness_timestamp_ms=int((time.time() - 15) * 1000)
    )
    assert stale_context.is_fresh is False
    assert stale_context.age_ms >= 15000

    # AwarenessReactionPlanner must return empty guidance for stale context
    ReactionBudgetManager.reset_budget()
    guidance = AwarenessReactionPlanner.build_awareness_prompt_guidance(stale_context)
    assert guidance == ""


def test_gate_va4_visual_focus_target_resolution():
    """
    Gate VA4: Resolves VisualFocusTarget for natural gaze shifting between user face and active objects.
    """
    # Case 1: User face present
    target_user = EnvironmentAwarenessEngine.resolve_visual_focus_target(
        user_detected=True,
        objects=[DetectedObject(type=SceneObjectType.CUP, confidence=0.9)]
    )
    assert target_user == VisualFocusTarget.USER_FACE

    # Case 2: User present with adorable Pet
    target_pet = EnvironmentAwarenessEngine.resolve_visual_focus_target(
        user_detected=True,
        objects=[DetectedObject(type=SceneObjectType.PET, confidence=0.85)]
    )
    assert target_pet == VisualFocusTarget.PET

    # Case 3: User looking away, Laptop active
    target_laptop = EnvironmentAwarenessEngine.resolve_visual_focus_target(
        user_detected=False,
        objects=[DetectedObject(type=SceneObjectType.LAPTOP, confidence=0.9)]
    )
    assert target_laptop == VisualFocusTarget.LAPTOP


def test_gate_va5_privacy_compliance_and_structured_dto_pipeline():
    """
    Gate VA5: Ephemeral pipeline produces strictly structured DTO without persisting raw image frames.
    """
    raw_payload = {
        "user_visible": True,
        "face_detected": True,
        "expression": "smiling",
        "objects": [{"label": "book", "confidence": 0.88}],
        "confidence": 0.95
    }

    # Process through coordinator
    context = AwarenessEngineCoordinator.process_vision_observation(raw_payload)

    assert isinstance(context, AwarenessContext)
    assert context.user_state.facial_emotion == FacialEmotionType.SMILING
    assert context.environment_state.detected_objects[0].type == SceneObjectType.BOOK
    assert AwarenessEngineCoordinator.get_current_awareness_context() is not None

    AwarenessEngineCoordinator.clear_cache()
    assert AwarenessEngineCoordinator.get_current_awareness_context() is None


def test_gate_va6_false_claim_prevention_and_suggestive_phrasing():
    """
    Gate VA6: Guidance is strictly suggestive, forbidding assertive factual claims (e.g. '너는 커피를 마신다').
    """
    ReactionBudgetManager.reset_budget()
    env = EnvironmentAwarenessState(
        detected_objects=[DetectedObject(type=SceneObjectType.CUP, confidence=0.89, label="cup")]
    )
    user = UserAwarenessState(face_detected=True, user_presence=True, facial_emotion=FacialEmotionType.SMILING)
    context = AwarenessContext(user_state=user, environment_state=env)

    guidance = AwarenessReactionPlanner.build_awareness_prompt_guidance(context)

    assert "[VISUAL COMPANION AWARENESS" in guidance
    assert "Suggestive Reaction" in guidance
    assert "NEVER sound like a surveillance camera" in guidance
    assert "DO NOT state '너는 커피를 마신다' as a definitive fact" in guidance


def test_gate_va7_awareness_non_intrusiveness_and_reaction_budget():
    """
    Gate VA7: Reaction Budget Manager enforces cooldowns and caps mentions to avoid intrusive user fatigue.
    """
    ReactionBudgetManager.reset_budget()

    # 1st mention: Allowed
    assert ReactionBudgetManager.can_mention_visual_context() is True
    ReactionBudgetManager.record_mention()

    # Immediate 2nd mention within 5 seconds: Blocked by cooldown
    assert ReactionBudgetManager.can_mention_visual_context() is False

    # Simulate multi-turn non-intrusiveness:
    # When budget blocked, build_awareness_prompt_guidance returns clean empty string
    context = AwarenessContext(
        user_state=UserAwarenessState(face_detected=True, facial_emotion=FacialEmotionType.SMILING)
    )
    assert AwarenessReactionPlanner.build_awareness_prompt_guidance(context) == ""
