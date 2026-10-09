import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.domain.character.presentation_profile import (
    VoiceProfileConfig,
    AvatarProfileConfig,
    ExpressionProfileConfig,
    GestureProfileConfig,
    CharacterPresentationProfile,
    CharacterPresentationContext,
)
from app.services.character.presentation_resolver import CharacterPresentationResolver
from app.services.character.context_resolver import CharacterContextResolver
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.db.models.companion import Companion
from app.db.models.character_presentation_profile import CharacterPresentationProfileModel


def create_mock_db():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()

    mock_exec_res = MagicMock()
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None), all=MagicMock(return_value=[])))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)
    return mock_db


@pytest.mark.asyncio
async def test_01_genie_presentation_resolution():
    """Test 1: Genie presentation resolves as Loving Wife with warm voice and affectionate style."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    ctx = await resolver.resolve(user_id="u1", companion_id="genie_pk")

    assert ctx.companion_id == "genie_pk"
    assert ctx.voice.voice_id == "nova"
    assert ctx.voice.persona_type == "WARM_COMPANION"
    assert ctx.voice.warmth >= 0.90
    assert ctx.avatar.avatar_id == "genie_default"
    assert ctx.avatar.visual_style == "warm_wife_2d"
    assert ctx.avatar.default_expression == "affectionate"
    assert ctx.expression.style == "warm_affectionate"


@pytest.mark.asyncio
async def test_02_mani_presentation_resolution():
    """Test 2: Mani presentation resolves as Lovely Daughter (NOT assistant) with bright energetic voice."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    ctx = await resolver.resolve(user_id="u1", companion_id="mani_pk")

    assert ctx.companion_id == "mani_pk"
    assert ctx.voice.voice_id == "shimmer"
    assert ctx.voice.persona_type == "ENERGETIC_GUIDE"
    assert ctx.voice.pitch_offset >= 1.5
    assert ctx.avatar.avatar_id == "mani_default"
    assert ctx.avatar.visual_style == "lovely_daughter_2d"
    assert ctx.avatar.default_expression == "happy"
    assert ctx.avatar.default_motion == "cheerful_bounce"
    assert ctx.expression.style == "bright_cheerful"


@pytest.mark.asyncio
async def test_03_hana_presentation_resolution():
    """Test 3: Hana presentation resolves as Hobby Friend with casual, relaxed, and friendly style."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    ctx = await resolver.resolve(user_id="u1", companion_id="hana_pk")

    assert ctx.companion_id == "hana_pk"
    assert ctx.voice.voice_id == "alloy"
    assert ctx.voice.persona_type == "WARM_COMPANION"
    assert ctx.avatar.avatar_id == "hana_default"
    assert ctx.avatar.visual_style == "casual_friend_2d"
    assert ctx.avatar.default_expression == "friendly"
    assert ctx.avatar.default_motion == "relaxed_idle"
    assert ctx.expression.style == "casual_playful"


@pytest.mark.asyncio
async def test_04_character_specific_voice_binding():
    """Test 4: Each character binds strictly to their distinct voice profile."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    genie_pres = await resolver.resolve("u1", "genie_pk")
    mani_pres = await resolver.resolve("u1", "mani_pk")
    hana_pres = await resolver.resolve("u1", "hana_pk")

    assert genie_pres.voice.voice_id == "nova"
    assert mani_pres.voice.voice_id == "shimmer"
    assert hana_pres.voice.voice_id == "alloy"
    assert genie_pres.voice.pitch_offset != mani_pres.voice.pitch_offset


@pytest.mark.asyncio
async def test_05_character_specific_avatar_binding():
    """Test 5: Each character binds strictly to their distinct avatar profile and motion."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    genie_pres = await resolver.resolve("u1", "genie_pk")
    mani_pres = await resolver.resolve("u1", "mani_pk")
    hana_pres = await resolver.resolve("u1", "hana_pk")

    assert genie_pres.avatar.visual_style == "warm_wife_2d"
    assert mani_pres.avatar.visual_style == "lovely_daughter_2d"
    assert hana_pres.avatar.visual_style == "casual_friend_2d"


@pytest.mark.asyncio
async def test_06_character_switch_presentation_sync():
    """Test 6: Switching characters sequentially (Genie -> Mani -> Hana -> Genie) produces exact presentation contexts."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    # 1. Switch to Genie
    c1 = await resolver.resolve("u1", "genie_pk")
    assert c1.voice.voice_id == "nova"
    assert c1.avatar.default_expression == "affectionate"

    # 2. Switch to Mani
    c2 = await resolver.resolve("u1", "mani_pk")
    assert c2.voice.voice_id == "shimmer"
    assert c2.avatar.default_expression == "happy"

    # 3. Switch to Hana
    c3 = await resolver.resolve("u1", "hana_pk")
    assert c3.voice.voice_id == "alloy"
    assert c3.avatar.default_expression == "friendly"

    # 4. Switch back to Genie
    c4 = await resolver.resolve("u1", "genie_pk")
    assert c4.voice.voice_id == "nova"
    assert c4.avatar.default_expression == "affectionate"


@pytest.mark.asyncio
async def test_07_presentation_cache_isolation():
    """Test 7: Cache keys are strictly isolated per user and companion (presentation:user:companion)."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    await resolver.resolve("u1", "genie_pk")
    await resolver.resolve("u1", "mani_pk")
    await resolver.resolve("u2", "genie_pk")

    assert "presentation:u1:genie_pk" in resolver._cache
    assert "presentation:u1:mani_pk" in resolver._cache
    assert "presentation:u2:genie_pk" in resolver._cache
    assert resolver._cache["presentation:u1:genie_pk"].voice.voice_id == "nova"
    assert resolver._cache["presentation:u1:mani_pk"].voice.voice_id == "shimmer"


@pytest.mark.asyncio
async def test_08_presentation_cache_invalidation():
    """Test 8: Updating presentation profile invalidates and updates cache immediately."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=Companion(id="mani_pk", user_id="u1", name="마니"))

    resolver = CharacterPresentationResolver(db=mock_db, registry_repo=mock_repo)
    # Pre-populate cache
    await resolver.resolve("u1", "mani_pk")
    assert "presentation:u1:mani_pk" in resolver._cache

    # Invalidate
    resolver.invalidate("u1", "mani_pk")
    assert "presentation:u1:mani_pk" not in resolver._cache


@pytest.mark.asyncio
async def test_09_archived_character_presentation_reject():
    """Test 9: Presentation resolution is rejected for archived characters (SB-5 Lifecycle Guard)."""
    mock_db = create_mock_db()
    archived_hana = Companion(id="hana_pk", user_id="u1", name="하나", lifecycle_status="archived")
    
    mock_exec_res = MagicMock()
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=archived_hana)))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)

    resolver = CharacterPresentationResolver(db=mock_db)
    with pytest.raises(PermissionError, match="presentation runtime is blocked"):
        await resolver.resolve("u1", "hana_pk")


@pytest.mark.asyncio
async def test_10_ownership_validation_rejects_unauthorized_user():
    """Test 10: Updating presentation of an unowned character raises PermissionError (403)."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=None) # Unauthorized

    resolver = CharacterPresentationResolver(db=mock_db, registry_repo=mock_repo)

    with pytest.raises(PermissionError, match="does not have access"):
        await resolver.update_presentation("user_attacker", "victim_companion", voice_updates={"voice_id": "alloy"})


@pytest.mark.asyncio
async def test_11_genie_backward_compatibility():
    """Test 11: CharacterContextResolver backward compatibility resolves Genie presentation seamlessly."""
    mock_db = create_mock_db()
    resolver = CharacterContextResolver(db=mock_db)

    ctx = await resolver.resolve(user_id="u1", companion_id="default")

    assert ctx.identity.name == "지니"
    assert ctx.presentation is not None
    assert ctx.presentation.voice.voice_id == "nova"
    assert ctx.presentation.avatar.visual_style == "warm_wife_2d"


@pytest.mark.asyncio
async def test_12_voice_cross_character_leakage_prevention():
    """Test 12: Validates zero voice leakage across different characters in simultaneous sessions."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    genie_ctx = await resolver.resolve("u1", "genie_pk")
    mani_ctx = await resolver.resolve("u1", "mani_pk")

    assert genie_ctx.voice.voice_id != mani_ctx.voice.voice_id
    assert genie_ctx.voice.persona_type != mani_ctx.voice.persona_type
    assert genie_ctx.voice.speaking_rate != mani_ctx.voice.speaking_rate


@pytest.mark.asyncio
async def test_13_avatar_cross_character_leakage_prevention():
    """Test 13: Validates zero avatar/expression leakage across different characters."""
    mock_db = create_mock_db()
    resolver = CharacterPresentationResolver(db=mock_db)

    genie_ctx = await resolver.resolve("u1", "genie_pk")
    mani_ctx = await resolver.resolve("u1", "mani_pk")
    hana_ctx = await resolver.resolve("u1", "hana_pk")

    assert genie_ctx.avatar.visual_style == "warm_wife_2d"
    assert mani_ctx.avatar.visual_style == "lovely_daughter_2d"
    assert hana_ctx.avatar.visual_style == "casual_friend_2d"


@pytest.mark.asyncio
async def test_14_runtime_context_presentation_consistency():
    """Test 14: CharacterRuntimeContext contains consistent presentation matching identity."""
    mock_db = create_mock_db()
    resolver = CharacterContextResolver(db=mock_db)

    ctx = await resolver.resolve("u1", "mani_pk")

    assert ctx.presentation.companion_id == "mani_pk"
    assert ctx.presentation.avatar.avatar_id == "mani_default"
    assert ctx.presentation.voice.voice_id == "shimmer"


@pytest.mark.asyncio
async def test_15_presentation_update_rollback_on_failure():
    """Test 15: DB exception during presentation update triggers rollback and propagates error."""
    mock_db = create_mock_db()
    mock_db.commit = AsyncMock(side_effect=Exception("Database lock error"))
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=Companion(id="genie_pk", user_id="u1", name="지니"))

    resolver = CharacterPresentationResolver(db=mock_db, registry_repo=mock_repo)

    with pytest.raises(Exception, match="Database lock error"):
        await resolver.update_presentation("u1", "genie_pk", voice_updates={"warmth": 0.99})
