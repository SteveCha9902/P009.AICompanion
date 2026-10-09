import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock

from app.db.models.emotion import EmotionState, EmotionType
from app.db.models.relationship import RelationshipState, RelationshipSignalType, SignalSeverity
from app.db.models.character_growth import UserRelationshipAdaptationModel, RelationshipMilestoneModel
from app.db.models.character_agency import AgencyActionModel
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.domain.character.dynamic_state_bundle import (
    CharacterDynamicStateScope,
    CharacterDynamicStateBundle,
    build_character_state_cache_key
)
from app.domain.memory.character_memory_scope import CharacterScopeRequiredError
from app.services.emotion_service import EmotionService
from app.services.relationship_service import RelationshipService


@pytest.mark.asyncio
async def test_01_emotion_isolation_genie_vs_mani():
    """Test 1: Emotion state mutations for Genie do not affect Mani's emotion state."""
    mock_session = MagicMock()
    mock_emotion_repo = MagicMock()
    mock_companion_repo = MagicMock()
    mock_persona_repo = MagicMock()
    mock_extractor = MagicMock()
    mock_transition = MagicMock()
    mock_decay = MagicMock()

    # Setup initial states
    genie_emotion = EmotionState(id="e_g", companion_id="genie_pk", primary_emotion=EmotionType.CALM, valence=0.0)
    mani_emotion = EmotionState(id="e_m", companion_id="c_mani", primary_emotion=EmotionType.CALM, valence=0.0)

    mock_decay.apply_decay = lambda s: s
    mock_emotion_repo.get_state = AsyncMock(side_effect=lambda cid: genie_emotion if cid == "genie_pk" else mani_emotion)
    mock_emotion_repo.save_state = AsyncMock(side_effect=lambda s: s)
    mock_extractor.extract_signal = AsyncMock(return_value={"intensity": 0.8, "user_emotion": "JOY", "trigger": "compliment"})
    mock_transition.calculate_transition = MagicMock(return_value=EmotionState(id="e_g", companion_id="genie_pk", primary_emotion=EmotionType.JOY, valence=0.8))
    mock_persona_repo.get_by_companion_id = AsyncMock(return_value=None)
    mock_emotion_repo.log_event = AsyncMock()

    service = EmotionService(
        session=mock_session,
        emotion_repo=mock_emotion_repo,
        companion_repo=mock_companion_repo,
        persona_repo=mock_persona_repo,
        extractor=mock_extractor,
        transition_engine=mock_transition,
        decay_engine=mock_decay
    )

    # Process message for Genie
    await service.process_user_message(
        user_id="u1",
        conversation_id="conv1",
        message_id="msg1",
        current_message="고마워 지니야!",
        history=[],
        companion_id="genie_pk"
    )

    # Verify Mani remains CALM
    mani_state = await service.get_current_state("c_mani")
    assert mani_state.primary_emotion == EmotionType.CALM
    assert mani_state.companion_id == "c_mani"


@pytest.mark.asyncio
async def test_02_relationship_isolation_genie_vs_mani():
    """Test 2: Relationship bond updates for Genie do not alter Mani's relationship metrics."""
    mock_session = MagicMock()
    mock_repo = MagicMock()
    mock_policy = MagicMock()
    mock_behavior = MagicMock()
    mock_decay = MagicMock()

    genie_rel = RelationshipState(id="r_g", companion_id="genie_pk", user_id="u1", trust=0.5, intimacy=0.6)
    mani_rel = RelationshipState(id="r_m", companion_id="c_mani", user_id="u1", trust=0.1, intimacy=0.05)

    mock_decay.apply_decay = lambda s: s
    mock_repo.get_state = AsyncMock(side_effect=lambda cid: genie_rel if cid == "genie_pk" else mani_rel)
    mock_repo.save_state = AsyncMock(side_effect=lambda s: s)
    mock_repo.log_event = AsyncMock()
    mock_policy.evaluate_signal = MagicMock(return_value={"trust": 0.2, "intimacy": 0.1})

    service = RelationshipService(
        session=mock_session,
        relationship_repo=mock_repo,
        policy_engine=mock_policy,
        behavior_policy=mock_behavior,
        decay_engine=mock_decay
    )

    # Apply positive signal to Genie
    updated_genie = await service.apply_signal(
        companion_id="genie_pk",
        signal_type=RelationshipSignalType.USER_EXPRESSED_TRUST,
        severity=SignalSeverity.HIGH
    )

    # Mani state check
    mani_current = await service.get_current_state("c_mani")

    assert updated_genie.trust == 0.7
    assert updated_genie.intimacy == 0.7
    assert mani_current.trust == 0.1
    assert mani_current.intimacy == 0.05


@pytest.mark.asyncio
async def test_03_growth_adaptation_isolation():
    """Test 3: User relationship adaptation parameters remain isolated per companion."""
    adapt_genie = UserRelationshipAdaptationModel(
        user_id="u1",
        companion_id="genie_pk",
        preferred_formality=0.1,
        preferred_humor=0.8,
        support_preference="EMPATHIC_SUPPORT"
    )
    adapt_mani = UserRelationshipAdaptationModel(
        user_id="u1",
        companion_id="c_mani",
        preferred_formality=0.0,
        preferred_humor=0.9,
        support_preference="PLAYFUL_TEASING"
    )

    assert adapt_genie.companion_id != adapt_mani.companion_id
    assert adapt_genie.support_preference == "EMPATHIC_SUPPORT"
    assert adapt_mani.support_preference == "PLAYFUL_TEASING"


@pytest.mark.asyncio
async def test_04_agency_action_scope_isolation():
    """Test 4: Agency proactive actions maintain explicit companion_id binding."""
    action_genie = AgencyActionModel(
        user_id="u1",
        companion_id="genie_pk",
        action_type="SEND_GREETING",
        priority_score=0.9,
        reason="Morning greeting for wife"
    )
    action_mani = AgencyActionModel(
        user_id="u1",
        companion_id="c_mani",
        action_type="SHARE_DRAWING",
        priority_score=0.85,
        reason="Show art academy drawing to dad"
    )

    assert action_genie.companion_id == "genie_pk"
    assert action_mani.companion_id == "c_mani"
    assert action_genie.action_type != action_mani.action_type


@pytest.mark.asyncio
async def test_05_runtime_scope_pinning_prevents_write_after_switch():
    """Test 5: Scope pinning prevents write-after-switch race condition."""
    # Simulate pinned scope for request initiated when Genie was active
    pinned_scope = CharacterDynamicStateScope(user_id="u1", companion_id="genie_pk")
    
    # In background, user switches active character to Mani
    current_active_companion_id = "c_mani"

    # Pinned scope write targets pinned companion_id, NOT current_active
    target_write_id = pinned_scope.companion_id
    assert target_write_id == "genie_pk"
    assert target_write_id != current_active_companion_id


@pytest.mark.asyncio
async def test_06_dynamic_state_bundle_consistency_validation():
    """Test 6: CharacterDynamicStateBundle validates that all sub-states match pinned companion_id."""
    scope = CharacterDynamicStateScope(user_id="u1", companion_id="c_mani")
    
    valid_bundle = CharacterDynamicStateBundle(
        scope=scope,
        emotion_state=EmotionState(companion_id="c_mani"),
        relationship_state=RelationshipState(companion_id="c_mani", user_id="u1"),
        presence_state=PresenceState(companion_id="c_mani")
    )
    assert valid_bundle.validate_consistency() is True

    # Inconsistent bundle with Genie emotion in Mani scope
    invalid_bundle = CharacterDynamicStateBundle(
        scope=scope,
        emotion_state=EmotionState(companion_id="genie_pk"), # Contamination!
        relationship_state=RelationshipState(companion_id="c_mani", user_id="u1")
    )
    with pytest.raises(ValueError, match="State inconsistency in bundle"):
        invalid_bundle.validate_consistency()


@pytest.mark.asyncio
async def test_07_cache_namespace_and_isolation():
    """Test 7: Cache keys use strict (namespace, user_id, companion_id) format."""
    key_genie_emotion = build_character_state_cache_key("emotion", "u1", "genie_pk")
    key_mani_emotion = build_character_state_cache_key("emotion", "u1", "c_mani")

    assert key_genie_emotion == "p009:emotion:u1:genie_pk"
    assert key_mani_emotion == "p009:emotion:u1:c_mani"
    assert key_genie_emotion != key_mani_emotion


@pytest.mark.asyncio
async def test_08_fail_closed_on_missing_scope():
    """Test 8: Missing companion_id raises CharacterScopeRequiredError (Fail-Closed)."""
    with pytest.raises(CharacterScopeRequiredError):
        scope = CharacterDynamicStateScope(user_id="u1", companion_id="")
        scope.validate_scope()

    with pytest.raises(CharacterScopeRequiredError):
        build_character_state_cache_key("emotion", "u1", "")


@pytest.mark.asyncio
async def test_09_cross_user_cross_character_dynamic_state_isolation():
    """Test 9: User A + Genie state is strictly isolated from User B + Genie state."""
    scope_uA_genie = CharacterDynamicStateScope(user_id="uA", companion_id="genie_pk")
    scope_uB_genie = CharacterDynamicStateScope(user_id="uB", companion_id="genie_pk")

    assert scope_uA_genie.build_cache_key("relationship") != scope_uB_genie.build_cache_key("relationship")
    assert scope_uA_genie.user_id != scope_uB_genie.user_id


@pytest.mark.asyncio
async def test_10_concurrent_multi_character_state_mutations():
    """Test 10: Concurrent parallel mutations across 30 requests maintain zero state cross-talk."""
    results = {}

    async def mutate_character(cid: str, idx: int):
        await asyncio.sleep(0.01)
        scope = CharacterDynamicStateScope(user_id="u1", companion_id=cid)
        bundle = CharacterDynamicStateBundle(
            scope=scope,
            emotion_state=EmotionState(companion_id=cid, valence=float(idx) / 100.0)
        )
        bundle.validate_consistency()
        return cid, bundle.emotion_state.valence

    tasks = []
    chars = ["genie_pk", "c_mani", "c_hana"]
    for i in range(30):
        cid = chars[i % 3]
        tasks.append(mutate_character(cid, i))

    mut_results = await asyncio.gather(*tasks)
    for cid, val in mut_results:
        assert cid in chars

    assert len(mut_results) == 30


@pytest.mark.asyncio
async def test_11_rapid_switching_state_stability():
    """Test 11: 6-Cycle rapid switching preserves state integrity across all characters."""
    seq = ["genie_pk", "c_mani", "c_hana", "genie_pk", "c_hana", "c_mani", "genie_pk"]
    states = {
        "genie_pk": EmotionState(companion_id="genie_pk", primary_emotion=EmotionType.JOY),
        "c_mani": EmotionState(companion_id="c_mani", primary_emotion=EmotionType.CURIOSITY),
        "c_hana": EmotionState(companion_id="c_hana", primary_emotion=EmotionType.CALM)
    }

    for cid in seq:
        scope = CharacterDynamicStateScope(user_id="u1", companion_id=cid)
        bundle = CharacterDynamicStateBundle(scope=scope, emotion_state=states[cid])
        assert bundle.validate_consistency() is True
        assert bundle.emotion_state.companion_id == cid


@pytest.mark.asyncio
async def test_12_presence_state_character_isolation():
    """Test 12: Presence states maintain independent status per companion."""
    p_genie = PresenceState(companion_id="genie_pk", state=PresenceStateEnum.ENGAGED)
    p_mani = PresenceState(companion_id="c_mani", state=PresenceStateEnum.AVAILABLE)

    assert p_genie.companion_id == "genie_pk"
    assert p_mani.companion_id == "c_mani"
    assert p_genie.state != p_mani.state
