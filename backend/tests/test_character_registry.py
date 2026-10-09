import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from app.db.models.companion import Companion
from app.db.models.user_character_preference import UserCharacterPreference
from app.domain.character.character_summary import CharacterSummary
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.context_resolver import CharacterContextResolver
from app.services.companion.domain import NormalizedInput, InputType
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.state.interaction_state import InteractionStateMachine


class InMemoryRegistryDB:
    """In-memory DB simulation for registry tests."""
    def __init__(self):
        self.companions = []
        self.preferences = {}

    async def execute(self, stmt):
        pass

    def add(self, entity):
        if isinstance(entity, Companion):
            self.companions.append(entity)
        elif isinstance(entity, UserCharacterPreference):
            self.preferences[entity.user_id] = entity

    async def commit(self):
        pass

    async def refresh(self, entity):
        pass


@pytest.mark.asyncio
async def test_01_existing_genie_registration():
    """Test 1: Existing Genie companion PK is preserved and mapped to active preference."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    # Simulate DB with existing Genie companion PK "genie_pk_999"
    genie_companion = Companion(id="genie_pk_999", user_id="user_1", name="지니")
    mock_repo.list_by_user = AsyncMock(return_value=[genie_companion])
    mock_repo.get_preference = AsyncMock(return_value=None) # No preference initially
    
    pref_created = UserCharacterPreference(id="pref_1", user_id="user_1", active_companion_id="genie_pk_999")
    mock_repo.set_active_companion = AsyncMock(return_value=pref_created)

    service = CharacterRegistryService(mock_repo, mock_db)
    active_id = await service.get_active_companion_id("user_1")

    assert active_id == "genie_pk_999"
    mock_repo.set_active_companion.assert_called_once_with("user_1", "genie_pk_999")


@pytest.mark.asyncio
async def test_02_list_characters():
    """Test 2: List characters correctly marks is_active flag."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    c1 = Companion(id="genie_1", user_id="user_1", name="지니")
    c2 = Companion(id="sua_1", user_id="user_1", name="수아")
    
    mock_repo.list_by_user = AsyncMock(return_value=[c1, c2])
    mock_repo.get_preference = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="user_1", active_companion_id="sua_1")
    )

    service = CharacterRegistryService(mock_repo, mock_db)
    summaries = await service.list_characters("user_1")

    assert len(summaries) == 2
    assert summaries[0].companion_id == "genie_1"
    assert summaries[0].is_active is False
    assert summaries[1].companion_id == "sua_1"
    assert summaries[1].is_active is True


@pytest.mark.asyncio
async def test_03_get_active_character():
    """Test 3: Get active character returns the active summary."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    c1 = Companion(id="genie_1", user_id="user_1", name="지니")
    mock_repo.list_by_user = AsyncMock(return_value=[c1])
    mock_repo.get_preference = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="user_1", active_companion_id="genie_1")
    )

    service = CharacterRegistryService(mock_repo, mock_db)
    active_id = await service.get_active_companion_id("user_1")
    summaries = await service.list_characters("user_1")
    active_summary = next(s for s in summaries if s.is_active)

    assert active_id == "genie_1"
    assert active_summary.name == "지니"
    assert active_summary.is_active is True


@pytest.mark.asyncio
async def test_04_ownership_validation_rejection():
    """Test 4: Ownership validation rejects unauthorized companion activation."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    # User 1 does NOT own companion "user2_sua"
    mock_repo.get_owned_companion = AsyncMock(return_value=None)

    service = CharacterRegistryService(mock_repo, mock_db)
    
    with pytest.raises(PermissionError, match="does not have access"):
        await service.set_active_companion("user_1", "user2_sua")


@pytest.mark.asyncio
async def test_05_switch_character():
    """Test 5: Switch character updates active companion atomically."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    sua_companion = Companion(id="sua_pk", user_id="user_1", name="수아")
    mock_repo.get_owned_companion = AsyncMock(return_value=sua_companion)
    mock_repo.set_active_companion = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="user_1", active_companion_id="sua_pk")
    )

    service = CharacterRegistryService(mock_repo, mock_db)
    summary = await service.set_active_companion("user_1", "sua_pk")

    assert summary.companion_id == "sua_pk"
    assert summary.name == "수아"
    assert summary.is_active is True
    assert service._active_companion_cache["user_1"] == "sua_pk"


@pytest.mark.asyncio
async def test_06_resolver_cache_isolation_on_switch():
    """Test 6: Resolver cache retains individual contexts and correctly resolves new active companion."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    genie = Companion(id="genie_pk", user_id="user_1", name="지니")
    sua = Companion(id="sua_pk", user_id="user_1", name="수아")
    
    mock_repo.list_by_user = AsyncMock(return_value=[genie, sua])
    # Initial preference: Genie
    pref = UserCharacterPreference(id="p1", user_id="user_1", active_companion_id="genie_pk")
    mock_repo.get_preference = AsyncMock(return_value=pref)
    mock_repo.get_owned_companion = AsyncMock(return_value=sua)
    
    service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=service)

    # 1. Resolve Active (Genie)
    ctx1 = await resolver.resolve(user_id="user_1", companion_id=None)
    assert ctx1.scope.companion_id == "genie_pk"
    assert ("user_1", "genie_pk") in resolver._cache

    # 2. Switch to Sua
    mock_repo.set_active_companion = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="user_1", active_companion_id="sua_pk")
    )
    await service.set_active_companion("user_1", "sua_pk")

    # 3. Resolve Active (Should now resolve Sua without dirty cache)
    ctx2 = await resolver.resolve(user_id="user_1", companion_id=None)
    assert ctx2.scope.companion_id == "sua_pk"
    assert ("user_1", "sua_pk") in resolver._cache
    # Genie cache is preserved for future use
    assert ("user_1", "genie_pk") in resolver._cache


@pytest.mark.asyncio
async def test_07_backward_compatibility_pipeline():
    """Test 7: process_message without companion_id uses dynamic active character."""
    event_bus = CompanionEventBus()
    state_machine = InteractionStateMachine(companion_id="genie_pk")
    
    mock_cb = AsyncMock()
    mock_cb.build.return_value = [{"role": "system", "content": "You are Genie"}]
    
    mock_llm = MagicMock()
    async def mock_stream(context):
        yield "반가워요!"
    mock_llm.stream = mock_stream

    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    mock_repo.get_preference = AsyncMock(
        return_value=UserCharacterPreference(id="p1", user_id="legacy_user", active_companion_id="genie_pk")
    )
    
    service = CharacterRegistryService(mock_repo, mock_db)
    resolver = CharacterContextResolver(db=None, registry_service=service)
    
    orchestrator = CompanionOrchestrator(
        event_bus=event_bus,
        state_machine=state_machine,
        context_builder=mock_cb,
        llm_provider=mock_llm,
        context_resolver=resolver
    )

    user_input = NormalizedInput(
        user_id="legacy_user",
        conversation_id="conv_1",
        content="안녕!",
        input_type=InputType.TEXT
    )

    events = []
    async for e in orchestrator.process_interaction(user_input):
        events.append(e)

    assert any("interaction_started" in e and '"companion_id": "genie_pk"' in e for e in events)


@pytest.mark.asyncio
async def test_08_no_context_leakage_between_switched_characters():
    """Test 8: Strict isolation of memory scope, voice profile between switched characters."""
    resolver = CharacterContextResolver(db=None)

    genie_ctx = await resolver.resolve("user_1", "genie_pk")
    sua_ctx = await resolver.resolve("user_1", "sua_pk")

    assert genie_ctx.memory_scope.companion_id == "genie_pk"
    assert sua_ctx.memory_scope.companion_id == "sua_pk"
    assert genie_ctx.voice_profile.voice_id != sua_ctx.voice_profile.voice_id
    assert genie_ctx.identity.name != sua_ctx.identity.name


@pytest.mark.asyncio
async def test_09_legacy_preference_bootstrap():
    """Test 9: Lazy bootstrap creates preference seamlessly and idempotently."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    genie_comp = Companion(id="legacy_genie_id", user_id="user_legacy", name="지니")
    mock_repo.list_by_user = AsyncMock(return_value=[genie_comp])
    mock_repo.get_preference = AsyncMock(return_value=None)
    
    pref = UserCharacterPreference(id="pref_new", user_id="user_legacy", active_companion_id="legacy_genie_id")
    mock_repo.set_active_companion = AsyncMock(return_value=pref)

    service = CharacterRegistryService(mock_repo, mock_db)
    
    # First call: Bootstrap triggers
    id1 = await service.get_active_companion_id("user_legacy")
    assert id1 == "legacy_genie_id"
    assert mock_repo.set_active_companion.call_count == 1

    # Second call: Cache / existing preference used without duplicate insertion
    id2 = await service.get_active_companion_id("user_legacy")
    assert id2 == "legacy_genie_id"
    assert mock_repo.set_active_companion.call_count == 1


@pytest.mark.asyncio
async def test_10_concurrent_switching_safety():
    """Test 10: Concurrent switching attempts resolve safely to single preference."""
    mock_db = MagicMock()
    mock_repo = CharacterRegistryRepository(mock_db)
    
    sua = Companion(id="sua_id", user_id="user_conc", name="수아")
    hana = Companion(id="hana_id", user_id="user_conc", name="하나")
    
    mock_repo.get_owned_companion = AsyncMock(side_effect=lambda u, cid: sua if cid == "sua_id" else hana)
    
    created_prefs = {}
    async def mock_set_active(u, cid):
        p = UserCharacterPreference(id="p_unique", user_id=u, active_companion_id=cid)
        created_prefs[u] = p
        return p
    mock_repo.set_active_companion = AsyncMock(side_effect=mock_set_active)

    service = CharacterRegistryService(mock_repo, mock_db)

    # Concurrent activate calls for Sua and Hana
    res_sua, res_hana = await asyncio.gather(
        service.set_active_companion("user_conc", "sua_id"),
        service.set_active_companion("user_conc", "hana_id")
    )

    # Exactly one user preference key exists for user_conc
    assert len(created_prefs) == 1
    assert "user_conc" in created_prefs
    assert created_prefs["user_conc"].active_companion_id in ["sua_id", "hana_id"]
