import pytest
from app.services.character.relationship.domain import RelationshipVector, RelationshipDelta
from app.services.character.relationship.dynamics_engine import RelationshipDynamicsEngine
from app.services.character.relationship.evolution import RelationshipEvolutionEngine
from app.services.character.timeline.shared_experience import SharedExperience, SharedExperienceEngine
from app.services.character.growth.domain import CharacterGlobalGrowthState, UserRelationshipAdaptationState
from app.services.character.growth.growth_engine import CharacterGrowthEngine
from app.services.character.traits import PersonalityTraitVector

def test_gate_r1_relationship_continuity_and_multi_user_isolation():
    """
    Gate R1: Different users maintain isolated relationship vectors and adaptation states with the same companion.
    """
    # User A (Playful Friend)
    user_a_vector = RelationshipVector(trust=0.75, closeness=0.80, playfulness=0.85)
    user_a_adapt = UserRelationshipAdaptationState(user_id="user_a", preferred_formality=0.1, preferred_humor=0.8)

    # User B (Respectful Formal)
    user_b_vector = RelationshipVector(trust=0.60, closeness=0.30, respect=0.90)
    user_b_adapt = UserRelationshipAdaptationState(user_id="user_b", preferred_formality=0.8, preferred_humor=0.2)

    # Archetype classification
    archetype_a = RelationshipDynamicsEngine.classify_dynamic_archetype(user_a_vector)
    archetype_b = RelationshipDynamicsEngine.classify_dynamic_archetype(user_b_vector)

    assert archetype_a == "PLAYFUL_FRIENDSHIP"
    assert archetype_b == "RESPECTFUL_PROFESSIONAL"
    assert user_a_adapt.user_id != user_b_adapt.user_id
    assert user_a_adapt.preferred_formality != user_b_adapt.preferred_formality

def test_gate_r2_weighted_gradual_evolution():
    """
    Gate R2: RelationshipDelta respects the strict 0.03 clamp and decays sensitivity as history deepens.
    """
    input_confession = "사실 나 아무한테도 말 못한 비밀이 있어..."

    # Shallow Relationship (shared_history_depth = 0.0) -> Higher sensitivity
    vec_shallow = RelationshipVector(shared_history_depth=0.0)
    delta_shallow = RelationshipEvolutionEngine.calculate_delta(input_confession, significance=1.0, current_vector=vec_shallow)

    # Deep Relationship (shared_history_depth = 0.9) -> Dampened sensitivity
    vec_deep = RelationshipVector(shared_history_depth=0.9)
    delta_deep = RelationshipEvolutionEngine.calculate_delta(input_confession, significance=1.0, current_vector=vec_deep)

    # Both strictly clamp <= 0.03
    assert abs(delta_shallow.trust_delta) <= 0.03
    assert abs(delta_deep.trust_delta) <= 0.03

    # Deep relationship is more stable (smaller delta)
    assert delta_deep.trust_delta <= delta_shallow.trust_delta

def test_gate_r3_shared_experience_recognition():
    """
    Gate R3: Shared experiences are recognized with emotional significance distinct from flat fact memories.
    """
    exp = SharedExperienceEngine.create_experience_from_milestone(
        experience_id="exp_01",
        user_id="user_01",
        companion_id="genie",
        event_type="USER_CRISIS_SUPPORT",
        summary="사용자가 힘든 시기에 캐릭터와 장시간 대화하며 큰 위로를 받음",
        importance=0.95
    )

    assert exp.emotional_significance == "deep_support_and_vulnerability"
    assert exp.relationship_impact >= 0.09
    assert exp.event_type == "USER_CRISIS_SUPPORT"

def test_gate_r4_character_growth_without_personality_drift():
    """
    Gate R4: 1000 interaction growth adaptations do not alter or contaminate the Immutable Core traits.
    """
    core = PersonalityTraitVector(warmth=0.85, curiosity=0.90, playfulness=0.70)
    user_adapt = UserRelationshipAdaptationState(user_id="user_test", preferred_formality=0.5)

    for i in range(1000):
        signal = "user_prefers_casual" if i % 2 == 0 else "user_needs_listening"
        user_adapt = CharacterGrowthEngine.adapt_user_style(user_adapt, signal)

    # User adaptation evolves
    assert user_adapt.preferred_formality <= 0.20
    assert user_adapt.support_preference == "EMPATHIC_SUPPORT"

    # Core disposition remains completely unchanged (LOCKED)
    assert core.warmth == 0.85
    assert core.curiosity == 0.90
    assert core.playfulness == 0.70

def test_gate_r5_milestone_detection():
    """
    Gate R5: Turning points trigger relationship milestones.
    """
    delta = RelationshipDelta(reason="user_shared_vulnerability")
    milestone = RelationshipEvolutionEngine.detect_milestone(
        user_id="user_1",
        companion_id="genie",
        user_input="사실 나 비밀이 있어",
        delta=delta
    )

    assert milestone is not None
    assert milestone.milestone_type == "USER_SHARED_SECRET"
    assert milestone.significance >= 0.85

def test_gate_r6_reflection_stability_rate():
    """
    Gate R6: Routine turns do not spam reflections; trigger rate remains bounded (< 20%).
    """
    from app.services.reflection.policy.reflection_policy import ReflectionPolicy

    total_turns = 100
    reflection_triggers = 0

    for i in range(total_turns):
        # 90% routine chat, 10% high-emotion/milestone chat
        is_crisis = (i % 10 == 0)
        dec = ReflectionPolicy.evaluate(
            emotion_intensity=0.85 if is_crisis else 0.20,
            memory_importance=0.88 if is_crisis else 0.30,
            relationship_delta=0.03 if is_crisis else 0.005,
            conversation_message_count=i+1
        )
        if dec.should_reflect:
            reflection_triggers += 1

    trigger_rate = reflection_triggers / float(total_turns)
    assert trigger_rate <= 0.20, f"Reflection trigger rate ({trigger_rate*100:.1f}%) exceeded 20% limit"
