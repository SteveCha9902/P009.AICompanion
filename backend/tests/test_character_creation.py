import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.domain.character.creation_request import CharacterCreationRequest
from app.domain.character.creation_result import CharacterCreationResult
from app.services.character.template_registry import CharacterTemplateRegistry
from app.services.character.personality_compiler import PersonalityCompiler
from app.services.character.character_factory import CharacterFactory
from app.services.character.creation_validator import (
    CharacterCreationValidator,
    CharacterValidationError,
    CharacterDuplicateNameError
)
from app.services.character.creation_service import CharacterCreationService
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.context_resolver import CharacterContextResolver
from app.db.models.companion import Companion
from app.db.models.user_character_preference import UserCharacterPreference


@pytest.mark.asyncio
async def test_01_create_professional_assistant():
    """Test 1: Create a professional assistant character with full DNA and initial state."""
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[
        Companion(id="genie_pk", user_id="u1", name="지니")
    ])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)

    req = CharacterCreationRequest(
        user_id="u1",
        name="수아",
        template_id="professional_assistant",
        role_title="AI 전문 비서",
        relationship_type="professional",
        mbti="ENTJ",
        personality_keywords=["논리적", "유능한", "친절한"],
        speaking_style="professional_polite",
        voice_id="female_korean_business_01",
        avatar_preset="business_female_01"
    )

    result = await service.create_character(req)

    assert result.name == "수아"
    assert result.role_title == "AI 전문 비서"
    assert result.is_active is False
    assert result.status == "created"
    assert result.dna.personality.mbti_type == "ENTJ"
    assert result.dna.personality.assertiveness >= 0.80
    assert result.dna.personality.intellectuality >= 0.85
    assert mock_db.add.call_count == 9 # Companion, Profile, Personality, Values, Emotion, Relationship, Avatar, Presentation, CharacterVersion(V1)
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_02_template_mbti_keyword_compilation():
    """Test 2: PersonalityCompiler synthesizes Template + MBTI + Keywords correctly."""
    template = CharacterTemplateRegistry.get_template("professional_assistant")
    
    # ENTJ + Keywords
    compiled = PersonalityCompiler.compile(
        template=template,
        mbti="ENTJ",
        keywords=["논리적", "유능한", "친절한"]
    )

    assert compiled.mbti_type == "ENTJ"
    assert compiled.assertiveness >= 0.80
    assert compiled.intellectuality >= 0.85
    assert compiled.conscientiousness >= 0.85
    assert compiled.warmth >= 0.65  # Boosted by "친절한" keyword


@pytest.mark.asyncio
async def test_03_character_isolation_genie_vs_sua():
    """Test 3: Newly created Sua DNA and Scope are strictly isolated from Genie."""
    req_sua = CharacterCreationRequest(
        user_id="u1",
        name="수아",
        template_id="professional_assistant",
        mbti="ENTJ"
    )
    template_sua = CharacterTemplateRegistry.get_template("professional_assistant")
    pers_sua = PersonalityCompiler.compile(template_sua, "ENTJ", ["논리적"])
    dna_sua = CharacterFactory.build_character_dna("sua_id", req_sua, template_sua, pers_sua)

    req_genie = CharacterCreationRequest(
        user_id="u1",
        name="지니",
        template_id="romantic_partner",
        mbti="INFJ"
    )
    template_genie = CharacterTemplateRegistry.get_template("romantic_partner")
    pers_genie = PersonalityCompiler.compile(template_genie, "INFJ", ["따뜻한"])
    dna_genie = CharacterFactory.build_character_dna("genie_id", req_genie, template_genie, pers_genie)

    assert dna_sua.identity.name != dna_genie.identity.name
    assert dna_sua.personality.mbti_type != dna_genie.personality.mbti_type
    assert dna_sua.personality.assertiveness > dna_genie.personality.assertiveness
    assert dna_genie.personality.warmth > dna_sua.personality.warmth
    assert dna_sua.voice_id != dna_genie.voice_id


@pytest.mark.asyncio
async def test_04_transaction_rollback_on_failure():
    """Test 4: Transaction failure during creation rolls back all changes with no partial data."""
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock(side_effect=Exception("DB Connection Timeout"))
    mock_db.rollback = AsyncMock()

    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)

    req = CharacterCreationRequest(user_id="u1", name="하나", mbti="ENFP")

    with pytest.raises(Exception, match="DB Connection Timeout"):
        await service.create_character(req)

    assert mock_db.rollback.called


@pytest.mark.asyncio
async def test_05_invalid_mbti_validation_error():
    """Test 5: Invalid MBTI type raises CharacterValidationError."""
    req = CharacterCreationRequest(user_id="u1", name="테스트", mbti="ABCD")
    
    with pytest.raises(CharacterValidationError, match="Invalid MBTI type"):
        CharacterCreationValidator.validate(req, existing_companion_names=[])


@pytest.mark.asyncio
async def test_06_duplicate_name_policy_conflict():
    """Test 6: Duplicate companion name for same user raises CharacterDuplicateNameError."""
    req = CharacterCreationRequest(user_id="u1", name="지니")
    
    with pytest.raises(CharacterDuplicateNameError, match="already exists"):
        CharacterCreationValidator.validate(req, existing_companion_names=["지니", "수아"])


@pytest.mark.asyncio
async def test_07_new_character_inactive_preserves_active():
    """Test 7: Created character is inactive by default; active preference is unaffected."""
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    # Active character is Genie
    pref = UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_preference = AsyncMock(return_value=pref)
    mock_repo.list_by_user = AsyncMock(return_value=[
        Companion(id="genie_pk", user_id="u1", name="지니")
    ])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    registry_service = CharacterRegistryService(mock_repo, mock_db)

    req = CharacterCreationRequest(user_id="u1", name="수아", mbti="ENTJ")
    result = await service.create_character(req)

    assert result.is_active is False
    # Active companion remains Genie
    active_cid = await registry_service.get_active_companion_id("u1")
    assert active_cid == "genie_pk"


@pytest.mark.asyncio
async def test_08_create_activate_runtime_resolve():
    """Test 8: Full workflow: Create -> Activate -> CharacterContextResolver resolves new character."""
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    genie_comp = Companion(id="genie_pk", user_id="u1", name="지니")
    created_sua_id = "sua_pk_100"
    sua_comp = Companion(id=created_sua_id, user_id="u1", name="수아")

    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[genie_comp, sua_comp])
    mock_repo.get_owned_companion = AsyncMock(return_value=sua_comp)
    
    pref = UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    mock_repo.get_preference = AsyncMock(return_value=pref)

    registry_service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=registry_service)

    # 1. Activate newly created Sua
    mock_repo.set_active_companion = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="u1", active_companion_id=created_sua_id)
    )
    await registry_service.set_active_companion("u1", created_sua_id)

    # 2. Runtime Context Resolver resolves Sua
    ctx = await resolver.resolve(user_id="u1", companion_id=None)
    assert ctx.scope.companion_id == created_sua_id
    assert ctx.identity.name == "수아"
    assert ctx.identity.display_name == "Sua"
    assert "sua" in ctx.voice_profile.voice_id
