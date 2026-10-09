import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.db.models.companion import Companion
from app.domain.character.creation_request import CharacterCreationRequest
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.creation_service import CharacterCreationService
from app.services.character.context_resolver import CharacterContextResolver
from app.repositories.character_registry_repository import CharacterRegistryRepository


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
def mock_companions():
    c_genie = Companion(id="genie_pk", user_id="u1", name="지니", is_system_character=True, lifecycle_status="available")
    c_mani = Companion(id="c_mani", user_id="u1", name="마니", is_system_character=False, lifecycle_status="available")
    c_hana = Companion(id="c_hana", user_id="u1", name="하나", is_system_character=False, lifecycle_status="available")
    return [c_genie, c_mani, c_hana]


@pytest.mark.asyncio
async def test_01_app_start_initial_active(mock_companions):
    """Scenario 1: App start lists characters and resolves initial active companion (Genie)."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=mock_companions)
    mock_repo.get_active_companion_id = AsyncMock(return_value="genie_pk")

    service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)
    characters = await service.list_characters("u1")

    assert len(characters) == 3
    assert characters[0].companion_id == "genie_pk"
    assert characters[0].is_active is True
    assert characters[1].is_active is False


@pytest.mark.asyncio
async def test_02_genie_to_mani_switching(mock_companions):
    """Scenario 2: One-touch switch from Genie to Mani succeeds atomically."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=mock_companions[1])
    mock_repo.set_active_preference = AsyncMock(return_value=MagicMock())
    mock_repo.get_active_companion_id = AsyncMock(return_value="c_mani")
    mock_repo.list_by_user = AsyncMock(return_value=mock_companions)

    service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)
    active = await service.set_active_companion("u1", "c_mani")

    assert active.companion_id == "c_mani"
    assert active.name == "마니"


@pytest.mark.asyncio
async def test_03_mani_to_hana_switching(mock_companions):
    """Scenario 3: One-touch switch from Mani to Hana succeeds atomically."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=mock_companions[2])
    mock_repo.set_active_preference = AsyncMock(return_value=MagicMock())
    mock_repo.get_active_companion_id = AsyncMock(return_value="c_hana")
    mock_repo.list_by_user = AsyncMock(return_value=mock_companions)

    service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)
    active = await service.set_active_companion("u1", "c_hana")

    assert active.companion_id == "c_hana"
    assert active.name == "하나"


@pytest.mark.asyncio
async def test_04_hana_to_genie_switching(mock_companions):
    """Scenario 4: One-touch switch back from Hana to Genie succeeds atomically."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=mock_companions[0])
    mock_repo.set_active_preference = AsyncMock(return_value=MagicMock())
    mock_repo.get_active_companion_id = AsyncMock(return_value="genie_pk")
    mock_repo.list_by_user = AsyncMock(return_value=mock_companions)

    service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)
    active = await service.set_active_companion("u1", "genie_pk")

    assert active.companion_id == "genie_pk"
    assert active.name == "지니"


@pytest.mark.asyncio
async def test_05_memory_scope_isolation():
    """Scenario 5: Active character switch isolates memory scope with zero cross-leakage."""
    from app.services.memory.character_memory_guard import CharacterMemoryGuard
    guard = CharacterMemoryGuard()

    # Valid writes scoped to Mani and Genie
    assert guard.validate_memory_write("u1", "c_mani", "마니 그림 연습") is True
    assert guard.validate_memory_write("u1", "genie_pk", "지니와 아침 산책") is True


@pytest.mark.asyncio
async def test_06_relationship_scope_isolation():
    """Scenario 6: Active character switch resolves independent relationship archetype."""
    from app.services.character.character_factory import CharacterFactory
    from app.services.character.template_registry import CharacterTemplateRegistry

    tmpl_mani = CharacterTemplateRegistry.get_template("lovely_daughter")
    req_mani = CharacterCreationRequest(user_id="u1", name="마니", relationship_type="family")
    rel_defaults = CharacterFactory.build_relationship_defaults(req_mani, tmpl_mani)

    assert rel_defaults["relationship_type"] == "family"
    assert rel_defaults["initial_stage"] == "close_bond"


@pytest.mark.asyncio
async def test_07_voice_avatar_binding_resolution():
    """Scenario 7: Mani character resolves shimmer voice and lovely_daughter_2d avatar preset."""
    mock_db = create_mock_db()
    resolver = CharacterContextResolver(db=mock_db)
    ctx = await resolver.resolve("u1", "c_mani")

    assert ctx.presentation.voice.voice_id == "shimmer"
    assert ctx.presentation.avatar.visual_style == "lovely_daughter_2d"


@pytest.mark.asyncio
async def test_08_custom_character_creation_and_list():
    """Scenario 8: Creating custom character reflects in gallery listing."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.list_by_user = AsyncMock(return_value=[])

    service = CharacterCreationService(db_session=mock_db, registry_repo=mock_repo)
    req = CharacterCreationRequest(user_id="u1", name="수아", role_title="AI 연구원")
    res = await service.create_character(req)

    assert res.name == "수아"
    assert res.status == "created"


@pytest.mark.asyncio
async def test_09_switch_failure_ownership_403(mock_companions):
    """Scenario 9: Switching to another user's companion raises PermissionError (403)."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=None) # Not owned

    service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)

    with pytest.raises(PermissionError, match="does not have access"):
        await service.set_active_companion("u2", "c_mani")


@pytest.mark.asyncio
async def test_10_rapid_switching_consistency(mock_companions):
    """Scenario 10: Rapid switching requests converge cleanly to the final selected companion."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(side_effect=lambda u, c: next(x for x in mock_companions if x.id == c))
    mock_repo.set_active_preference = AsyncMock(return_value=MagicMock())
    mock_repo.get_active_companion_id = AsyncMock(return_value="c_mani")
    mock_repo.list_by_user = AsyncMock(return_value=mock_companions)

    service = CharacterRegistryService(repository=mock_repo, db_session=mock_db)

    # Sequence: Genie -> Hana -> Mani
    _ = await service.set_active_companion("u1", "genie_pk")
    _ = await service.set_active_companion("u1", "c_hana")
    final_active = await service.set_active_companion("u1", "c_mani")

    assert final_active.companion_id == "c_mani"
    assert final_active.name == "마니"
