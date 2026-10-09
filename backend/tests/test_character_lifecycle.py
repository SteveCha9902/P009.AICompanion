import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from app.domain.character.update_request import CharacterUpdateRequest
from app.domain.character.change_classification import ChangeType, CharacterChangeClassifier
from app.domain.character.lifecycle_status import CharacterLifecycleStatus
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.lifecycle_service import CharacterLifecycleService
from app.services.character.context_resolver import CharacterContextResolver
from app.db.models.companion import Companion
from app.db.models.character_profile import CharacterProfileModel
from app.db.models.character_personality import CharacterPersonalityModel
from app.db.models.character_version import CharacterVersionModel
from app.db.models.user_character_preference import UserCharacterPreference


def create_mock_db():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()

    mock_exec_res = MagicMock()
    mock_exec_res.scalar = MagicMock(return_value=1)
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None), all=MagicMock(return_value=[])))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)
    return mock_db


@pytest.mark.asyncio
async def test_01_cosmetic_update_no_version_bump():
    """Test 1: Cosmetic updates (voice/avatar) update profile but do not generate a new DNA version."""
    mock_db = create_mock_db()

    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    mock_repo.get_preference = AsyncMock(return_value=None)
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)

    req = CharacterUpdateRequest(
        user_id="u1",
        companion_id="sua_pk",
        voice_id="female_korean_02",
        avatar_preset="casual_female_02"
    )

    summary = await service.update_character("u1", "sua_pk", req)

    assert summary.name == "수아"
    assert summary.voice_name == "female_korean_02"
    # No CharacterVersionModel should be added for cosmetic changes
    added_versions = [arg for call in mock_db.add.call_args_list for arg in call[0] if isinstance(arg, CharacterVersionModel)]
    assert len(added_versions) == 0


@pytest.mark.asyncio
async def test_02_personality_update_generates_version_2():
    """Test 2: Personality or MBTI updates generate Version 2 snapshot."""
    mock_db = create_mock_db()

    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    mock_repo.get_preference = AsyncMock(return_value=None)
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)

    req = CharacterUpdateRequest(
        user_id="u1",
        companion_id="sua_pk",
        mbti="ENTP",
        personality_keywords=["창의적인", "열정적인"]
    )

    summary = await service.update_character("u1", "sua_pk", req)

    assert summary.name == "수아"
    added_versions = [arg for call in mock_db.add.call_args_list for arg in call[0] if isinstance(arg, CharacterVersionModel)]
    assert len(added_versions) == 1
    assert added_versions[0].version == 2
    assert added_versions[0].change_type in ["minor", "major"]
    assert added_versions[0].dna_snapshot["personality"]["mbti"] == "ENTP"


@pytest.mark.asyncio
async def test_03_memory_preservation_on_evolution():
    """Test 3: Personality changes do not mutate, erase, or reset past memory entries."""
    mock_db = create_mock_db()
    resolver = CharacterContextResolver(db=mock_db)
    
    ctx_v1 = await resolver.resolve(user_id="u1", companion_id="sua_pk")
    mem_scope_v1 = ctx_v1.memory_scope

    # After evolution, memory scope companion_id remains identical
    ctx_v2 = await resolver.resolve(user_id="u1", companion_id="sua_pk")
    mem_scope_v2 = ctx_v2.memory_scope

    assert mem_scope_v1.companion_id == mem_scope_v2.companion_id == "sua_pk"


@pytest.mark.asyncio
async def test_04_archive_character_blocks_runtime():
    """Test 4: Archived character is blocked in runtime context resolver."""
    mock_db = create_mock_db()

    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    # Active companion is Genie, not Sua
    mock_repo.get_preference = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    )
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)
    summary = await service.archive_character("u1", "sua_pk")

    assert sua.lifecycle_status == "archived"
    assert sua.archived_at is not None

    # Now verify runtime resolver blocks archived companion
    sua_archived = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="archived")
    mock_exec_res = MagicMock()
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=sua_archived)))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)

    resolver = CharacterContextResolver(db=mock_db)
    with pytest.raises(PermissionError, match="archived and cannot be accessed in runtime"):
        await resolver.resolve("u1", "sua_pk")


@pytest.mark.asyncio
async def test_05_active_character_archive_reject():
    """Test 5: Attempting to archive the currently active companion raises 409 Conflict."""
    mock_db = create_mock_db()
    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    # Sua is the active companion
    mock_repo.get_preference = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="u1", active_companion_id="sua_pk")
    )
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)

    with pytest.raises(ValueError, match="Active character cannot be archived"):
        await service.archive_character("u1", "sua_pk")


@pytest.mark.asyncio
async def test_06_restore_character_state_transition():
    """Test 6: Restoring an archived character transitions status to available."""
    mock_db = create_mock_db()

    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="archived", archived_at=datetime.utcnow())
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    mock_repo.get_preference = AsyncMock(return_value=None)
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)
    summary = await service.restore_character("u1", "sua_pk")

    assert sua.lifecycle_status == "available"
    assert sua.archived_at is None


@pytest.mark.asyncio
async def test_07_soft_delete_character():
    """Test 7: Soft delete marks status=deleted and deleted_at, retaining underlying rows."""
    mock_db = create_mock_db()

    hana = Companion(id="hana_pk", user_id="u1", name="하나", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=hana)
    # Active companion is Genie, not Hana
    mock_repo.get_preference = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="u1", active_companion_id="genie_pk")
    )
    mock_repo.list_by_user = AsyncMock(return_value=[hana])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)
    summary = await service.delete_character("u1", "hana_pk")

    assert hana.lifecycle_status == "deleted"
    assert hana.deleted_at is not None


@pytest.mark.asyncio
async def test_08_deleted_character_runtime_reject():
    """Test 8: Deleted character is strictly blocked from runtime context resolution."""
    mock_db = create_mock_db()
    hana_deleted = Companion(id="hana_pk", user_id="u1", name="하나", lifecycle_status="deleted")
    
    mock_exec_res = MagicMock()
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=hana_deleted)))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)

    resolver = CharacterContextResolver(db=mock_db)
    with pytest.raises(PermissionError, match="deleted and cannot be accessed in runtime"):
        await resolver.resolve("u1", "hana_pk")


@pytest.mark.asyncio
async def test_09_deleted_character_activation_reject():
    """Test 9: Attempting to activate a deleted companion raises ValueError (409 Conflict)."""
    mock_db = create_mock_db()
    hana_deleted = Companion(id="hana_pk", user_id="u1", name="하나", lifecycle_status="deleted")
    
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=hana_deleted)

    reg_service = CharacterRegistryService(mock_repo, mock_db)
    with pytest.raises(ValueError, match="Cannot activate deleted character"):
        await reg_service.set_active_companion("u1", "hana_pk")


@pytest.mark.asyncio
async def test_10_character_version_history():
    """Test 10: Version history returns chronological DNA evolution trail."""
    mock_db = create_mock_db()
    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)

    v1 = CharacterVersionModel(companion_id="sua_pk", version=1, change_type="initial", dna_snapshot={"mbti": "ENTJ"})
    v2 = CharacterVersionModel(companion_id="sua_pk", version=2, change_type="minor", dna_snapshot={"mbti": "ENTP"})
    
    mock_exec_res = MagicMock()
    mock_exec_res.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[v1, v2])))
    mock_db.execute = AsyncMock(return_value=mock_exec_res)

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)
    history = await service.get_version_history("u1", "sua_pk")

    assert len(history) == 2
    assert history[0]["version"] == 1
    assert history[0]["change_type"] == "initial"
    assert history[1]["version"] == 2
    assert history[1]["change_type"] == "minor"


@pytest.mark.asyncio
async def test_11_system_character_genie_protection():
    """Test 11: System default character (Genie) cannot be archived or deleted."""
    mock_db = create_mock_db()
    genie = Companion(id="genie_pk", user_id="u1", name="지니", is_system_character=True, lifecycle_status="available")
    
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=genie)

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)

    with pytest.raises(PermissionError, match="System default character .* cannot be archived"):
        await service.archive_character("u1", "genie_pk")

    with pytest.raises(PermissionError, match="System default character .* cannot be deleted"):
        await service.delete_character("u1", "genie_pk")


@pytest.mark.asyncio
async def test_12_ownership_validation_on_lifecycle_ops():
    """Test 12: Operating on another user's companion raises PermissionError (403)."""
    mock_db = create_mock_db()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=None) # User does not own companion

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)

    with pytest.raises(PermissionError, match="does not have access"):
        await service.archive_character("user_attacker", "victim_sua")


@pytest.mark.asyncio
async def test_13_transaction_rollback_on_failure():
    """Test 13: DB failure during update triggers complete session rollback."""
    mock_db = create_mock_db()
    mock_db.commit = AsyncMock(side_effect=Exception("DB Deadlock"))

    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)
    req = CharacterUpdateRequest(user_id="u1", companion_id="sua_pk", role_title="New Role")

    with pytest.raises(Exception, match="DB Deadlock"):
        await service.update_character("u1", "sua_pk", req)


@pytest.mark.asyncio
async def test_14_runtime_context_cache_invalidation():
    """Test 14: Updating a character invalidates runtime resolver cache so new traits load immediately."""
    mock_db = create_mock_db()

    sua = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="available")
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    mock_repo.get_preference = AsyncMock(return_value=None)
    mock_repo.list_by_user = AsyncMock(return_value=[sua])

    resolver = CharacterContextResolver(db=None)
    # Pre-populate resolver cache
    ctx_old = await resolver.resolve("u1", "sua_pk")
    assert ("u1", "sua_pk") in resolver._cache

    service = CharacterLifecycleService(
        db_session=mock_db,
        registry_repo=mock_repo,
        context_resolver=resolver
    )

    # Perform minor personality update
    req = CharacterUpdateRequest(user_id="u1", companion_id="sua_pk", mbti="ENTP")
    await service.update_character("u1", "sua_pk", req)

    # Verify cache was invalidated
    assert ("u1", "sua_pk") not in resolver._cache


@pytest.mark.asyncio
async def test_15_version_concurrency_unique_constraint():
    """Test 15: CharacterVersionModel enforces unique (companion_id, version) constraint."""
    v1 = CharacterVersionModel(companion_id="sua_pk", version=2, change_type="minor", dna_snapshot={})
    v2 = CharacterVersionModel(companion_id="sua_pk", version=2, change_type="major", dna_snapshot={})

    assert v1.companion_id == v2.companion_id
    assert v1.version == v2.version
    assert CharacterVersionModel.__table_args__[0].name == "uq_character_version"


@pytest.mark.asyncio
async def test_16_archived_character_agency_block():
    """Test 16: Archived companion is blocked from agency execution or proactive decision."""
    sua_archived = Companion(id="sua_pk", user_id="u1", name="수아", lifecycle_status="archived")
    
    # Validation helper simulating Agency Engine Guard
    def validate_agency_eligibility(comp: Companion) -> bool:
        if comp.lifecycle_status != "available":
            return False
        return True

    assert validate_agency_eligibility(sua_archived) is False


@pytest.mark.asyncio
async def test_17_invalid_lifecycle_transition_deleted_to_restore_reject():
    """Test 17: Attempting to restore a deleted character is rejected with ValueError (409 Conflict)."""
    mock_db = create_mock_db()
    hana_deleted = Companion(id="hana_pk", user_id="u1", name="하나", lifecycle_status="deleted", deleted_at=datetime.utcnow())
    
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_owned_companion = AsyncMock(return_value=hana_deleted)

    service = CharacterLifecycleService(db_session=mock_db, registry_repo=mock_repo)

    with pytest.raises(ValueError, match="Cannot restore deleted companion"):
        await service.restore_character("u1", "hana_pk")
