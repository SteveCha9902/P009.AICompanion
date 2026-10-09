import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock

from app.domain.relationship.relationship_dimensions import RelationshipDimensions
from app.domain.relationship.relationship_stage import RelationshipStage
from app.domain.relationship.relationship_event import RelationshipEventType
from app.domain.relationship.relationship_state import RelationshipState
from app.domain.relationship.relationship_anchor import RelationshipAnchor, RelationshipAnchorType

from app.services.relationship.relationship_event_detector import RelationshipEventDetector
from app.services.relationship.relationship_change_calculator import RelationshipChangeCalculator, MAX_DELTA_PER_INTERACTION
from app.services.relationship.relationship_stage_resolver import RelationshipStageResolver
from app.services.relationship.relationship_context_compiler import RelationshipContextCompiler

def test_gate_r1_and_r6_multi_dimensions_and_rate_limit():
    """
    Gate R1 & R6: 7-Dimensional Social Bond evolution with strict delta limit (delta <= 0.03).
    """
    initial_dims = RelationshipDimensions(
        familiarity=0.1,
        trust=0.1,
        affection=0.1,
        intimacy=0.05,
        respect=0.3,
        comfort=0.1,
        attachment=0.05
    )

    # Trigger multiple high-impact events simultaneously
    events = [
        RelationshipEventType.PERSONAL_STORY_SHARED,
        RelationshipEventType.USER_SHOWED_TRUST,
        RelationshipEventType.USER_EXPRESSED_AFFECTION
    ]

    deltas = RelationshipChangeCalculator.calculate_deltas(events, initial_dims)

    # Verify each dimension delta obeys MAX_DELTA_PER_INTERACTION
    for dim, delta in deltas.items():
        assert delta <= MAX_DELTA_PER_INTERACTION, f"Delta for {dim} exceeded max limit: {delta}"
        assert delta >= -MAX_DELTA_PER_INTERACTION

    # Intimacy and trust must have grown positive
    assert deltas["intimacy"] > 0
    assert deltas["trust"] > 0
    assert deltas["affection"] > 0

def test_gate_r2_and_r3_stage_resolver_no_sudden_jump():
    """
    Gate R2 & R3: Stage promotion requires multi-criteria threshold satisfaction (No single-score jump).
    """
    # 1. High trust alone is NOT enough for CLOSE_FRIEND without sufficient intimacy and conversations
    premature_dims = RelationshipDimensions(
        familiarity=0.3,
        trust=0.9, # abnormally high
        affection=0.3,
        intimacy=0.1,
        comfort=0.2
    )
    stage = RelationshipStageResolver.resolve_stage(premature_dims, total_conversations=3)
    assert stage == RelationshipStage.ACQUAINTANCE # Cannot jump to CLOSE_FRIEND

    # 2. Balanced mature bond satisfies CLOSE_FRIEND
    mature_dims = RelationshipDimensions(
        familiarity=0.70,
        trust=0.65,
        comfort=0.60,
        intimacy=0.50,
        respect=0.70
    )
    stage_mature = RelationshipStageResolver.resolve_stage(mature_dims, total_conversations=20)
    assert stage_mature == RelationshipStage.CLOSE_FRIEND

def test_gate_r7_long_absence_decay_preserves_core():
    """
    Gate R7: Long absence (30 days) reduces presence and familiarity slightly but preserves core trust and memories.
    """
    initial_dims = RelationshipDimensions(
        familiarity=0.80,
        trust=0.85,
        comfort=0.75,
        respect=0.80
    )

    decay = RelationshipChangeCalculator.apply_decay(initial_dims, days_absent=30.0)

    # Core trust must barely decay
    assert abs(decay["trust"]) <= 0.01
    assert decay["respect"] == 0.0

    # Familiarity and comfort decay slowly
    assert decay["familiarity"] < 0
    assert decay["comfort"] < 0

def test_gate_r4_and_r8_context_compiler_and_safety_boundary():
    """
    Gate R4 & R8: Relationship context must be compiled without numbers and enforce strict anti-dependency safety boundary.
    """
    state = RelationshipState(
        user_id="u-1",
        companion_id="c-1",
        stage=RelationshipStage.CLOSE_FRIEND,
        total_conversations=42,
        recent_presence=1.0
    )

    anchors = [
        RelationshipAnchor(
            user_id="u-1",
            companion_id="c-1",
            anchor_type=RelationshipAnchorType.FIRST_PERSONAL_CONFESSION,
            summary="사용자가 깊은 고민을 털어놓았던 날.",
            importance=0.9
        )
    ]

    compiled = RelationshipContextCompiler.compile(state, anchors)

    # 1. Qualitative stage is injected
    assert "[RELATIONSHIP CONTEXT — SOCIAL BOND]" in compiled
    assert "Close Friend" in compiled
    assert "사용자가 깊은 고민을 털어놓았던 날" in compiled

    # 2. Strict Safety Boundaries are mandatorily enforced
    assert "[RELATIONSHIP SAFETY BOUNDARIES]" in compiled
    assert "Never exhibit possessiveness, jealousy, or claim exclusivity" in compiled
    assert "Never encourage emotional dependency or isolation" in compiled
    assert "Always celebrate and respect the user's personal autonomy" in compiled
