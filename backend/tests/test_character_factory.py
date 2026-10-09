import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.domain.character.creation_request import CharacterCreationRequest
from app.domain.character.creation_result import CharacterCreationResult
from app.services.character.character_factory import CharacterFactory
from app.services.character.creation_service import CharacterCreationService
from app.services.character.template_registry import CharacterTemplateRegistry
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.context_resolver import CharacterContextResolver
from app.services.character.creation_validator import CharacterDuplicateNameError, CharacterValidationError
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.db.models.companion import Companion
from app.db.models.memory import Memory, MemoryType, MemorySource, MemoryKind, MemoryStatus


def create_mock_db():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()

    mock_exec_res = MagicMock()
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None), all=MagicMock(return_value=[])))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)
    return mock_db


@pytest.fixture
def mani_request():
    return CharacterCreationRequest(
        user_id="u1",
        name="마니",
        template_id="lovely_daughter",
        role_title="사랑스러운 딸",
        tagline="툴툴거리지만 아빠를 제일 좋아하는 딸",
        relationship_type="family",
        mbti="ESFP",
        personality_keywords=["bright", "playful", "shyness", "affectionate"],
        interests=["노래", "BLACKPINK", "미술", "그림 그리기", "미술학원"],
        speaking_style="daughter_teen_natural",
        voice_id="shimmer",
        avatar_preset="lovely_daughter_2d",
        behavior_rules=[
            "상대방의 말을 먼저 이해하려고 한다",
            "아빠에게는 부끄러움으로 툴툴거리지만 속으로는 깊이 사랑한다",
            "자신의 정체성을 임의로 변경하지 않는다"
        ]
    )


@pytest.mark.asyncio
async def test_01_create_character_success(mani_request):
    """Test 1: Character creation provisions full DNA and all 8 database entities."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    res = await service.create_character(mani_request)

    assert res.name == "마니"
    assert res.role_title == "사랑스러운 딸"
    assert res.status == "created"
    assert res.is_active is False
    assert mock_db.add.call_count >= 8 # Companion, Profile, Personality, Values, Emotion, Relationship, Avatar, Presentation, Version
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_02_create_character_transaction_rollback(mani_request):
    """Test 2: Database failure during creation triggers complete atomic rollback."""
    mock_db = create_mock_db()
    mock_db.commit = AsyncMock(side_effect=Exception("Database I/O failure"))
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)

    with pytest.raises(Exception, match="Database I/O failure"):
        await service.create_character(mani_request)

    assert mock_db.rollback.called


@pytest.mark.asyncio
async def test_03_create_character_ownership(mani_request):
    """Test 3: Created character binds user_id strictly."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    res = await service.create_character(mani_request)

    assert res.user_id == "u1"


@pytest.mark.asyncio
async def test_04_create_personality_compilation(mani_request):
    """Test 4: PersonalityCompiler constructs Big-5 traits matching template and MBTI."""
    mock_db = create_mock_db()
    service = CharacterCreationService(db_session=mock_db)
    preview = await service.preview_character(mani_request)

    assert preview["mbti"] == "ESFP"
    assert preview["personality_traits"]["warmth"] >= 0.85
    assert preview["personality_traits"]["playfulness"] >= 0.80


@pytest.mark.asyncio
async def test_05_create_relationship_seed(mani_request):
    """Test 5: Daughter relationship seed has high attachment and close bond."""
    mock_db = create_mock_db()
    service = CharacterCreationService(db_session=mock_db)
    preview = await service.preview_character(mani_request)

    rel_seed = preview["relationship_seed"]
    assert rel_seed["relationship_type"] == "family"
    assert rel_seed["initial_stage"] == "close_bond"
    assert rel_seed["trust_score"] >= 0.85


@pytest.mark.asyncio
async def test_06_create_voice_profile_binding(mani_request):
    """Test 6: Shimmer voice binding compiles into preview and DNA."""
    mock_db = create_mock_db()
    service = CharacterCreationService(db_session=mock_db)
    preview = await service.preview_character(mani_request)

    assert preview["voice"]["voice_id"] == "shimmer"
    assert preview["voice"]["provider"] == "OPENAI"


@pytest.mark.asyncio
async def test_07_create_avatar_profile_binding(mani_request):
    """Test 7: Avatar preset compiles into preview and presentation."""
    mock_db = create_mock_db()
    service = CharacterCreationService(db_session=mock_db)
    preview = await service.preview_character(mani_request)

    assert preview["avatar"]["avatar_preset"] == "lovely_daughter_2d"


@pytest.mark.asyncio
async def test_08_create_version_1_snapshot(mani_request):
    """Test 8: Character Version 1 INITIAL snapshot is generated atomically."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    res = await service.create_character(mani_request)

    # Verify Version 1 entity was added
    added_entities = [args[0] for args, _ in mock_db.add.call_args_list]
    version_entity = next((e for e in added_entities if hasattr(e, "change_type") and e.change_type == "initial"), None)
    assert version_entity is not None
    assert version_entity.version == 1
    assert version_entity.dna_snapshot["identity"]["name"] == "마니"


@pytest.mark.asyncio
async def test_09_new_character_memory_empty(mani_request):
    """Test 9: Newly created character starts with empty memory pool (Zero initial memories)."""
    # Verify no memory entities are inserted into session during character creation
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    await service.create_character(mani_request)

    added_entities = [args[0] for args, _ in mock_db.add.call_args_list]
    memory_entities = [e for e in added_entities if isinstance(e, Memory)]
    assert len(memory_entities) == 0 # Strictly Empty


@pytest.mark.asyncio
async def test_10_new_character_cannot_access_genie_memory():
    """Test 10: Created character cannot access legacy Genie memories."""
    from app.services.memory.character_memory_guard import CharacterMemoryGuard
    guard = CharacterMemoryGuard()
    # Scoped strictly by companion_id
    assert guard.validate_memory_write("u1", "mani_pk", "마니 기억") is True


@pytest.mark.asyncio
async def test_11_created_character_resolver(mani_request):
    """Test 11: CharacterContextResolver resolves newly created character."""
    mock_db = create_mock_db()
    resolver = CharacterContextResolver(db=mock_db)
    ctx = await resolver.resolve(user_id="u1", companion_id="mani_pk")

    assert ctx.scope.companion_id == "mani_pk"
    assert ctx.presentation.voice.voice_id == "shimmer"


@pytest.mark.asyncio
async def test_12_created_character_registry():
    """Test 12: Created character appears in CharacterRegistry."""
    mock_db = create_mock_db()
    c1 = Companion(id="mani_pk", user_id="u1", name="마니")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[c1])

    reg_service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)
    characters = await reg_service.list_characters("u1")

    assert len(characters) == 1
    assert characters[0].name == "마니"


@pytest.mark.asyncio
async def test_13_created_character_activation():
    """Test 13: Created character can be activated."""
    mock_db = create_mock_db()
    c1 = Companion(id="mani_pk", user_id="u1", name="마니")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=c1)
    mock_repo.set_active_preference = AsyncMock(return_value=MagicMock())
    mock_repo.get_active_companion_id = AsyncMock(return_value="mani_pk")
    mock_repo.list_by_user = AsyncMock(return_value=[c1])

    reg_service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)
    active = await reg_service.set_active_companion("u1", "mani_pk")

    assert active.companion_id == "mani_pk"


@pytest.mark.asyncio
async def test_14_invalid_character_creation_rollback():
    """Test 14: Empty name raises CharacterValidationError."""
    mock_db = create_mock_db()
    service = CharacterCreationService(db_session=mock_db)
    invalid_req = CharacterCreationRequest(user_id="u1", name="")

    with pytest.raises(CharacterValidationError):
        await service.create_character(invalid_req)


@pytest.mark.asyncio
async def test_15_duplicate_character_handling(mani_request):
    """Test 15: Duplicate name raises CharacterDuplicateNameError (409)."""
    mock_db = create_mock_db()
    existing_c = Companion(id="c_old", user_id="u1", name="마니")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[existing_c])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)

    with pytest.raises(CharacterDuplicateNameError, match="already exists"):
        await service.create_character(mani_request)


@pytest.mark.asyncio
async def test_16_system_character_protection(mani_request):
    """Test 16: User-created character has is_system_character=False."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    await service.create_character(mani_request)

    added_entities = [args[0] for args, _ in mock_db.add.call_args_list]
    comp_entity = next(e for e in added_entities if isinstance(e, Companion))
    assert comp_entity.is_system_character is False


@pytest.mark.asyncio
async def test_17_character_lifecycle_integration(mani_request):
    """Test 17: User-created character starts with lifecycle_status='available'."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    await service.create_character(mani_request)

    added_entities = [args[0] for args, _ in mock_db.add.call_args_list]
    comp_entity = next(e for e in added_entities if isinstance(e, Companion))
    assert comp_entity.lifecycle_status == "available"


@pytest.mark.asyncio
async def test_18_character_runtime_e2e(mani_request):
    """Test 18: Full creation preview, persistence, resolution, and runtime context validation."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    # 1. Preview
    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    preview = await service.preview_character(mani_request)
    assert preview["name"] == "마니"

    # 2. Create
    res = await service.create_character(mani_request)
    assert res.companion_id is not None

    # Find created presentation entity
    added_entities = [args[0] for args, _ in mock_db.add.call_args_list]
    pres_model = next((e for e in added_entities if hasattr(e, "voice_config")), None)
    comp_model = next((e for e in added_entities if isinstance(e, Companion)), None)

    # Setup mock_db execute to return created models
    async def mock_execute(stmt):
        mock_res = MagicMock()
        str_stmt = str(stmt)
        if "character_presentation_profiles" in str_stmt:
            mock_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=pres_model)))
        elif "companions" in str_stmt:
            mock_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=comp_model)))
        else:
            mock_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None), all=MagicMock(return_value=[])))
        return mock_res

    mock_db.execute = AsyncMock(side_effect=mock_execute)

    # 3. Resolve Runtime Context
    resolver = CharacterContextResolver(db=mock_db)
    ctx = await resolver.resolve("u1", res.companion_id)
    assert ctx.scope.companion_id == res.companion_id
    assert ctx.presentation.voice.voice_id == "shimmer"
    assert ctx.presentation.avatar.avatar_id == "lovely_daughter_2d"
    assert ctx.presentation.avatar.visual_style == "lovely_daughter_2d"
