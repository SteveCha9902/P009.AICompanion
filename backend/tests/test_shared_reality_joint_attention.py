import pytest
import time
from app.domain.awareness.awareness_context import (
    AwarenessContext,
    SceneObjectType,
    DetectedObject,
    BoundingBox,
    EnvironmentAwarenessState
)
from app.domain.shared_reality.shared_reality_context import (
    SharedRealityContext,
    JointAttentionState,
    UserConfirmationStatus,
    AttentionAnchor,
    CandidateFocus
)
from app.services.shared_reality.deictic_resolver import DeicticResolutionEngine
from app.services.shared_reality.user_intent_estimator import UserIntentEstimator
from app.services.shared_reality.focus_persistence_manager import FocusPersistenceManager
from app.services.shared_reality.joint_attention_engine import JointAttentionEngine
from app.services.shared_reality.shared_reality_planner import SharedRealityPlanner

def test_gate_sr1_focus_target_detection_via_deictic_resolver():
    """
    Gate SR1: Deictic pointers ('이거 봐', '새로 산 컵') are parsed and matched with visual objects.
    """
    assert DeicticResolutionEngine.has_deictic_intent("이거 봐봐 진짜 예쁘지?") is True
    assert DeicticResolutionEngine.has_deictic_intent("오늘 날씨 좋다") is False
    assert DeicticResolutionEngine.detect_explicit_object_mention("이 컵 새로 산거야") == SceneObjectType.CUP
    assert DeicticResolutionEngine.detect_explicit_object_mention("노트북 새로 샀어") == SceneObjectType.LAPTOP


def test_gate_sr2_joint_attention_formation_and_confidence_threshold():
    """
    Gate SR2: Shared Focus is formed ONLY if target confidence >= 0.75; otherwise falls back to User Focus.
    """
    FocusPersistenceManager.clear()
    
    # Case A: High confidence (0.88 >= 0.75) -> SHARED_FOCUS
    high_conf_objs = [DetectedObject(type=SceneObjectType.CUP, confidence=0.88, label="cup")]
    ctx_shared = JointAttentionEngine.evaluate_joint_attention(
        user_utterance="이거 봐",
        awareness_context=AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=high_conf_objs))
    )
    assert ctx_shared.state == JointAttentionState.SHARED_FOCUS
    assert ctx_shared.focus_target == SceneObjectType.CUP
    assert ctx_shared.shared_attention is True

    # Case B: Low confidence (0.55 < 0.75) -> USER_FOCUS
    FocusPersistenceManager.clear()
    low_conf_objs = [DetectedObject(type=SceneObjectType.LAPTOP, confidence=0.55, label="laptop")]
    ctx_user_only = JointAttentionEngine.evaluate_joint_attention(
        user_utterance="이거 봐",
        awareness_context=AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=low_conf_objs))
    )
    assert ctx_user_only.state == JointAttentionState.USER_FOCUS
    assert ctx_user_only.shared_attention is False


def test_gate_sr3_focus_persistence_and_lock():
    """
    Gate SR3: Focus Lock prevents jittering between alternate objects within 6 seconds.
    """
    FocusPersistenceManager.clear()
    
    # 1. Focus on Cup
    objs_turn1 = [DetectedObject(type=SceneObjectType.CUP, confidence=0.90, label="cup")]
    ctx1 = JointAttentionEngine.evaluate_joint_attention(
        user_utterance="이거 새로 샀어",
        awareness_context=AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=objs_turn1))
    )
    assert ctx1.focus_target == SceneObjectType.CUP
    assert ctx1.is_locked is True

    # 2. Next moment (1s later), Plant is detected with higher confidence
    objs_turn2 = [DetectedObject(type=SceneObjectType.PLANT, confidence=0.95, label="plant")]
    ctx2 = JointAttentionEngine.evaluate_joint_attention(
        user_utterance="색깔 어때?",
        awareness_context=AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=objs_turn2))
    )
    # Must remain locked on CUP to avoid rapid twitching
    assert ctx2.focus_target == SceneObjectType.CUP


def test_gate_sr4_gaze_alignment_and_abstract_anchor():
    """
    Gate SR4: Bounding boxes and object types map accurately to AttentionAnchor for resolution independence.
    """
    # Bottom right cup
    cup_obj = DetectedObject(
        type=SceneObjectType.CUP,
        confidence=0.89,
        bbox=BoundingBox(x_min=0.7, y_min=0.7, x_max=0.9, y_max=0.9)
    )
    primary, candidates, _, _ = UserIntentEstimator.estimate_focus_candidates("이거 봐", [cup_obj])
    assert primary.anchor == AttentionAnchor.LOWER_RIGHT

    # Bottom left book
    book_obj = DetectedObject(
        type=SceneObjectType.BOOK,
        confidence=0.85,
        bbox=BoundingBox(x_min=0.1, y_min=0.7, x_max=0.3, y_max=0.9)
    )
    primary_b, _, _, _ = UserIntentEstimator.estimate_focus_candidates("책 봐봐", [book_obj])
    assert primary_b.anchor == AttentionAnchor.LOWER_LEFT


def test_gate_sr5_shared_reality_dialogue_directive():
    """
    Gate SR5: Synthesizes Amy's shared reality dialogue directives with natural suggestive curiosity.
    """
    ctx = SharedRealityContext(
        state=JointAttentionState.SHARED_FOCUS,
        focus_target=SceneObjectType.CUP,
        target_label="cup",
        target_confidence=0.92,
        anchor=AttentionAnchor.LOWER_RIGHT,
        shared_attention=True
    )
    directive = SharedRealityPlanner.build_shared_reality_directive(ctx)
    assert "[SHARED REALITY & JOINT ATTENTION DIRECTIVE]" in directive
    assert "새로 산 컵이야? 디자인 깔끔하다" in directive
    assert "SHARED ATTENTION: CUP/DRINK" in directive


def test_gate_sr6_false_assumption_prevention():
    """
    Gate SR6: Forbids dogmatic definitive claims (e.g. '그건 100% 커피다').
    """
    ctx = SharedRealityContext(
        state=JointAttentionState.SHARED_FOCUS,
        focus_target=SceneObjectType.CUP,
        target_confidence=0.88,
        shared_attention=True
    )
    directive = SharedRealityPlanner.build_shared_reality_directive(ctx)
    assert "DO NOT state '그건 100% 커피다' as an absolute certainty" in directive


def test_gate_sr7_non_intrusive_15s_timeout():
    """
    Gate SR7: Automatically disengages joint attention back to NONE if no interaction occurs for 15 seconds.
    """
    FocusPersistenceManager.clear()
    
    # Create context with timestamp 20 seconds ago
    old_time = int((time.time() - 20) * 1000)
    ctx = SharedRealityContext(
        state=JointAttentionState.SHARED_FOCUS,
        focus_target=SceneObjectType.CUP,
        shared_attention=True,
        last_interaction_time_ms=old_time,
        focus_lock_until_ms=old_time + 6000
    )
    assert ctx.is_timed_out is True

    # FocusPersistenceManager should automatically clear timed-out context
    FocusPersistenceManager._current_context = ctx
    active = FocusPersistenceManager.get_current_context()
    assert active is None


def test_gate_sr8_wrong_focus_recovery():
    """
    Gate SR8: When user rejects AI's guess ('아니 책이야'), immediately clears lock and re-evaluates focus to Book.
    """
    FocusPersistenceManager.clear()
    
    # 1. Initial guess: Cup
    objs = [
        DetectedObject(type=SceneObjectType.CUP, confidence=0.85, label="cup"),
        DetectedObject(type=SceneObjectType.BOOK, confidence=0.82, label="book")
    ]
    ctx1 = JointAttentionEngine.evaluate_joint_attention("이거 봐", AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=objs)))
    assert ctx1.focus_target == SceneObjectType.CUP

    # 2. User correction: "아니 책이야"
    ctx_recovered = JointAttentionEngine.evaluate_joint_attention(
        "아니 책이야",
        AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=objs))
    )
    # Must immediately recover focus onto BOOK
    assert ctx_recovered.focus_target == SceneObjectType.BOOK
    assert ctx_recovered.state == JointAttentionState.SHARED_FOCUS


def test_gate_sr9_multi_object_scene_resolution():
    """
    Gate SR9: Multi-object scenes maintain Top 3 CandidateFocus and select appropriately based on explicit intent.
    """
    FocusPersistenceManager.clear()
    objs = [
        DetectedObject(type=SceneObjectType.LAPTOP, confidence=0.91, label="laptop"),
        DetectedObject(type=SceneObjectType.CUP, confidence=0.86, label="cup"),
        DetectedObject(type=SceneObjectType.BOOK, confidence=0.80, label="book"),
        DetectedObject(type=SceneObjectType.PLANT, confidence=0.75, label="plant")
    ]

    # Explicit mention of Book among 4 objects
    ctx = JointAttentionEngine.evaluate_joint_attention(
        "이 책 내용 정말 감동적이야",
        AwarenessContext(environment_state=EnvironmentAwarenessState(detected_objects=objs))
    )
    assert ctx.focus_target == SceneObjectType.BOOK
    assert len(ctx.candidate_targets) == 3
    assert any(c.object_type == SceneObjectType.LAPTOP for c in ctx.candidate_targets)
