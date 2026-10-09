import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.db.models.memory import Memory, MemoryType, MemorySource, MemoryKind, MemoryStatus
from app.db.models.companion import Companion
from app.repositories.memory_repository import MemoryRepository
from app.services.memory.retriever import MemoryRetriever
from app.services.memory.character_memory_guard import CharacterMemoryGuard
from app.services.context.providers.memory_provider import MemoryContextProvider


def create_mock_embedding_provider():
    provider = MagicMock()
    provider.embed = AsyncMock(return_value=[0.1] * 1536)
    return provider


@pytest.fixture
def memory_fixture():
    """Generates distinct, isolated memories for Genie, Mani, and Hana."""
    genie_mem = Memory(
        id="mem_genie_1",
        companion_id="genie_pk",
        content="아빠와 엄마가 지난달 결혼기념일에 제주도 여행을 갔다.",
        type=MemoryType.IMPORTANT_EVENT,
        source=MemorySource.USER_EXPLICIT,
        kind=MemoryKind.PERSISTENT,
        status=MemoryStatus.ACTIVE,
        importance=90,
        confidence=1.0
    )
    mani_mem = Memory(
        id="mem_mani_1",
        companion_id="mani_pk",
        content="아빠가 지난주 토요일에 미술학원에 데려다줬고, BLACKPINK 신곡을 함께 들었다.",
        type=MemoryType.PERSONAL_FACT,
        source=MemorySource.USER_EXPLICIT,
        kind=MemoryKind.EPISODIC,
        status=MemoryStatus.ACTIVE,
        importance=85,
        confidence=1.0
    )
    hana_mem = Memory(
        id="mem_hana_1",
        companion_id="hana_pk",
        content="사용자와 후지필름 카메라 렌즈 및 출사 장소 이야기를 했다.",
        type=MemoryType.INTEREST,
        source=MemorySource.USER_EXPLICIT,
        kind=MemoryKind.PERSISTENT,
        status=MemoryStatus.ACTIVE,
        importance=70,
        confidence=1.0
    )
    return {"genie": genie_mem, "mani": mani_mem, "hana": hana_mem}


@pytest.mark.asyncio
async def test_01_genie_memory_isolation(memory_fixture):
    """Test 1: Genie retrieves only Genie's private memories."""
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_repo.search_similar = AsyncMock(return_value=[(memory_fixture["genie"], 0.95)])
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    res = await retriever.retrieve(companion_id="genie_pk", query="결혼기념일 여행")

    assert len(res) == 1
    assert "제주도 여행" in res[0].content
    assert res[0].companion_id == "genie_pk"
    mock_repo.search_similar.assert_called_once_with(
        companion_id="genie_pk",
        embedding=[0.1] * 1536,
        limit=15,
        threshold=0.60
    )


@pytest.mark.asyncio
async def test_02_mani_memory_isolation(memory_fixture):
    """Test 2: Mani retrieves only Mani's lovely daughter memories (art, BLACKPINK)."""
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_repo.search_similar = AsyncMock(return_value=[(memory_fixture["mani"], 0.92)])
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    res = await retriever.retrieve(companion_id="mani_pk", query="미술학원 이야기")

    assert len(res) == 1
    assert "미술학원" in res[0].content
    assert "BLACKPINK" in res[0].content
    assert res[0].companion_id == "mani_pk"


@pytest.mark.asyncio
async def test_03_hana_memory_isolation(memory_fixture):
    """Test 3: Hana retrieves only Hana's hobby memories (camera)."""
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_repo.search_similar = AsyncMock(return_value=[(memory_fixture["hana"], 0.88)])
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    res = await retriever.retrieve(companion_id="hana_pk", query="카메라 렌즈 이야기")

    assert len(res) == 1
    assert "카메라" in res[0].content
    assert res[0].companion_id == "hana_pk"


@pytest.mark.asyncio
async def test_04_cross_character_retrieval_prevention(memory_fixture):
    """Test 4: Querying Mani never returns Genie's or Hana's memories."""
    mock_repo = MagicMock(spec=MemoryRepository)
    
    # Simulate DB returning empty because companion_id != genie_pk
    async def mock_search(companion_id, embedding, limit, threshold):
        if companion_id == "mani_pk":
            return [(memory_fixture["mani"], 0.90)]
        return []

    mock_repo.search_similar = AsyncMock(side_effect=mock_search)
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    res = await retriever.retrieve(companion_id="mani_pk", query="우리 전에 뭐 했지?")

    assert len(res) == 1
    assert "제주도 여행" not in res[0].content # Zero Genie leakage
    assert "카메라" not in res[0].content # Zero Hana leakage
    assert "미술학원" in res[0].content


@pytest.mark.asyncio
async def test_05_cross_character_memory_write_prevention():
    """Test 5: Memory write without valid companion_id or empty content is strictly prevented."""
    guard = CharacterMemoryGuard()
    
    with pytest.raises(ValueError, match="companion_id is required"):
        guard.validate_memory_write("u1", companion_id="", content="기억 내용")
        
    with pytest.raises(ValueError, match="cannot be empty"):
        guard.validate_memory_write("u1", companion_id="mani_pk", content="")


@pytest.mark.asyncio
async def test_06_character_switch_memory_isolation(memory_fixture):
    """Test 6: Sequential switching (Genie -> Mani -> Hana -> Genie) produces strictly isolated memory contexts."""
    mock_repo = MagicMock(spec=MemoryRepository)
    
    async def mock_search(companion_id, embedding, limit, threshold):
        if companion_id == "genie_pk":
            return [(memory_fixture["genie"], 0.95)]
        elif companion_id == "mani_pk":
            return [(memory_fixture["mani"], 0.92)]
        elif companion_id == "hana_pk":
            return [(memory_fixture["hana"], 0.88)]
        return []

    mock_repo.search_similar = AsyncMock(side_effect=mock_search)
    mock_embed = create_mock_embedding_provider()
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)

    # 1. Switch to Genie
    g_res = await retriever.retrieve("genie_pk", "대화")
    assert "제주도" in g_res[0].content

    # 2. Switch to Mani
    m_res = await retriever.retrieve("mani_pk", "대화")
    assert "미술학원" in m_res[0].content

    # 3. Switch to Hana
    h_res = await retriever.retrieve("hana_pk", "대화")
    assert "카메라" in h_res[0].content

    # 4. Switch back to Genie
    g_res2 = await retriever.retrieve("genie_pk", "대화")
    assert "제주도" in g_res2[0].content


@pytest.mark.asyncio
async def test_07_context_builder_character_memory_isolation(memory_fixture):
    """Test 7: MemoryContextProvider injects only active character's memories."""
    mock_retriever = MagicMock(spec=MemoryRetriever)
    mock_retriever.retrieve = AsyncMock(return_value=[memory_fixture["mani"]])
    mock_repo = MagicMock()

    provider = MemoryContextProvider(
        memory_retriever=mock_retriever,
        companion_repo=mock_repo,
        user_id="u1",
        companion_id="mani_pk"
    )

    ctx = await provider.build_context("conv_1", "오늘 뭐 했어?")
    assert len(ctx) >= 1
    assert "미술학원" in ctx[0]["content"]
    assert "제주도" not in ctx[0]["content"]


@pytest.mark.asyncio
async def test_08_memory_extraction_character_binding():
    """Test 8: CharacterMemoryGuard validates memory creation binding parameters."""
    guard = CharacterMemoryGuard()
    is_valid = guard.validate_memory_write("u1", "mani_pk", "아빠가 그림 칭찬해줬음")
    assert is_valid is True


@pytest.mark.asyncio
async def test_09_archived_character_memory_access():
    """Test 9: Memory retrieval is blocked for archived companions (SB-5 Lifecycle Guard)."""
    mock_db = MagicMock()
    archived_companion = Companion(id="archived_c", user_id="u1", name="보관된캐릭터", lifecycle_status="archived")
    mock_exec = MagicMock()
    mock_exec.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=archived_companion)))
    mock_db.execute = AsyncMock(return_value=mock_exec)

    guard = CharacterMemoryGuard(db=mock_db)

    with pytest.raises(PermissionError, match="Memory retrieval blocked"):
        await guard.validate_retrieval_access(user_id="u1", companion_id="archived_c")


@pytest.mark.asyncio
async def test_10_ownership_validation_rejects_unauthorized_user():
    """Test 10: Unauthorized user cannot access companion memories."""
    mock_db = MagicMock()
    other_companion = Companion(id="c1", user_id="owner_user", name="다른사람캐릭터", lifecycle_status="available")
    mock_exec = MagicMock()
    mock_exec.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=other_companion)))
    mock_db.execute = AsyncMock(return_value=mock_exec)

    guard = CharacterMemoryGuard(db=mock_db)

    with pytest.raises(PermissionError, match="does not own companion"):
        await guard.validate_retrieval_access(user_id="attacker_user", companion_id="c1")


@pytest.mark.asyncio
async def test_11_legacy_genie_memory_compatibility(memory_fixture):
    """Test 11: Legacy default_companion queries resolve seamlessly to Genie."""
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_repo.search_similar = AsyncMock(return_value=[(memory_fixture["genie"], 0.95)])
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    res = await retriever.retrieve(companion_id="default_companion", query="결혼기념일")

    assert len(res) == 1
    assert "제주도" in res[0].content


@pytest.mark.asyncio
async def test_12_memory_retrieval_cache_isolation(memory_fixture):
    """Test 12: Cache keys are strictly isolated per (user_id, companion_id, query)."""
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_repo.search_similar = AsyncMock(return_value=[(memory_fixture["mani"], 0.90)])
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    
    # 1. First retrieve (populate cache)
    await retriever.retrieve("mani_pk", "미술학원", user_id="u1")
    assert "memory_cache:u1:mani_pk:미술학원" in retriever._cache

    # 2. Invalidate
    retriever.invalidate_cache("u1", "mani_pk")
    assert "memory_cache:u1:mani_pk:미술학원" not in retriever._cache


@pytest.mark.asyncio
async def test_13_embedding_search_character_isolation(memory_fixture):
    """Test 13: Vector search passes companion_id into repo search_similar."""
    mock_repo = MagicMock(spec=MemoryRepository)
    mock_repo.search_similar = AsyncMock(return_value=[(memory_fixture["hana"], 0.85)])
    mock_embed = create_mock_embedding_provider()

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)
    await retriever.retrieve(companion_id="hana_pk", query="출사")

    mock_repo.search_similar.assert_called_once_with(
        companion_id="hana_pk",
        embedding=[0.1] * 1536,
        limit=15,
        threshold=0.60
    )


@pytest.mark.asyncio
async def test_14_concurrent_character_interaction_isolation(memory_fixture):
    """Test 14: Concurrent queries for different characters execute without cross-talk."""
    mock_repo = MagicMock(spec=MemoryRepository)
    
    async def mock_search(companion_id, embedding, limit, threshold):
        await asyncio.sleep(0.01)
        if companion_id == "genie_pk":
            return [(memory_fixture["genie"], 0.95)]
        elif companion_id == "mani_pk":
            return [(memory_fixture["mani"], 0.90)]
        return []

    mock_repo.search_similar = AsyncMock(side_effect=mock_search)
    mock_embed = create_mock_embedding_provider()
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=mock_embed)

    g_task = retriever.retrieve("genie_pk", "query1")
    m_task = retriever.retrieve("mani_pk", "query2")

    g_res, m_res = await asyncio.gather(g_task, m_task)

    assert "제주도" in g_res[0].content
    assert "미술학원" in m_res[0].content


@pytest.mark.asyncio
async def test_15_no_character_id_failure_safety():
    """Test 15: Memory retrieval without companion_id fails safely with ValueError."""
    guard = CharacterMemoryGuard()
    with pytest.raises(ValueError, match="companion_id must not be empty"):
        await guard.validate_retrieval_access(user_id="u1", companion_id="")
