import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.db.models.memory import Memory, MemoryType, MemorySource, MemoryKind, MemoryStatus
from app.db.models.companion import Companion
from app.services.memory.retriever import MemoryRetriever
from app.services.memory.character_memory_guard import CharacterMemoryGuard
from app.services.memory.embedding import BaseEmbeddingProvider
from app.repositories.memory_repository import MemoryRepository
from app.services.context.providers.memory_provider import MemoryContextProvider


class MockEmbedding(BaseEmbeddingProvider):
    async def embed(self, text: str):
        return [0.1] * 1536

    async def embed_batch(self, texts: list):
        return [[0.1] * 1536 for _ in texts]


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
async def test_01_memory_write_character_scope():
    """Test 1: Memory write requires valid companion_id binding."""
    guard = CharacterMemoryGuard()
    assert guard.validate_memory_write("u1", "c_mani", "마니 그림 그리기 좋아함") is True


@pytest.mark.asyncio
async def test_02_memory_write_missing_companion_id_rejected():
    """Test 2: Memory write with missing companion_id raises ValueError."""
    guard = CharacterMemoryGuard()
    with pytest.raises(ValueError, match="companion_id is required"):
        guard.validate_memory_write("u1", "", "내용")


@pytest.mark.asyncio
async def test_03_memory_read_character_scope():
    """Test 3: Memory retrieval queries strictly filter by companion_id."""
    mock_repo = MagicMock()
    m1 = Memory(id="m1", companion_id="c_mani", content="마니 기억", type=MemoryType.FACT, importance=50, confidence=1.0, updated_at=datetime.utcnow())
    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [(m1, 0.95)] if companion_id == "c_mani" else [])

    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())
    results = await retriever.retrieve(companion_id="c_mani", query="기억", user_id="u1")

    assert len(results) == 1
    assert results[0].companion_id == "c_mani"


@pytest.mark.asyncio
async def test_04_direct_cross_character_retrieval_blocked():
    """Test 4: Requesting memory for Mani when only Genie memories exist returns 0 results."""
    mock_repo = MagicMock()
    m_genie = Memory(id="m_genie", companion_id="genie_pk", content="지니와의 아침 산책", importance=50, confidence=1.0, updated_at=datetime.utcnow())

    async def mock_search(companion_id, embedding, limit=15, threshold=0.60):
        if companion_id == "genie_pk":
            return [(m_genie, 0.9)]
        return []

    mock_repo.search_similar = AsyncMock(side_effect=mock_search)
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    # Query as Mani
    results = await retriever.retrieve(companion_id="c_mani", query="산책", user_id="u1")
    assert len(results) == 0 # Zero leakage


@pytest.mark.asyncio
async def test_05_vector_similarity_no_cross_leak():
    """Test 5: Semantically identical query returns strictly character-scoped vector records."""
    mock_repo = MagicMock()
    m_genie = Memory(id="m1", companion_id="genie_pk", content="아빠와 제주도 여행", importance=50, confidence=1.0, updated_at=datetime.utcnow())
    m_mani = Memory(id="m2", companion_id="c_mani", content="친구와 제주도 여행", importance=50, confidence=1.0, updated_at=datetime.utcnow())

    async def mock_search(companion_id, embedding, limit=15, threshold=0.60):
        if companion_id == "genie_pk":
            return [(m_genie, 0.92)]
        elif companion_id == "c_mani":
            return [(m_mani, 0.91)]
        return []

    mock_repo.search_similar = AsyncMock(side_effect=mock_search)
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    res_genie = await retriever.retrieve(companion_id="genie_pk", query="제주도 여행", user_id="u1")
    res_mani = await retriever.retrieve(companion_id="c_mani", query="제주도 여행", user_id="u1")

    assert res_genie[0].content == "아빠와 제주도 여행"
    assert res_mani[0].content == "친구와 제주도 여행"
    assert res_genie[0].companion_id != res_mani[0].companion_id


@pytest.mark.asyncio
async def test_06_memory_cache_character_isolation():
    """Test 6: Genie retrieval cache does not cause Cache HIT for Mani query."""
    mock_repo = MagicMock()
    m_genie = Memory(id="m1", companion_id="genie_pk", content="지니 비밀", importance=50, confidence=1.0, updated_at=datetime.utcnow())
    m_mani = Memory(id="m2", companion_id="c_mani", content="마니 비밀", importance=50, confidence=1.0, updated_at=datetime.utcnow())

    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [(m_genie, 0.9)] if companion_id == "genie_pk" else [(m_mani, 0.9)])
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    # 1. Warm cache for Genie
    _ = await retriever.retrieve(companion_id="genie_pk", query="비밀", user_id="u1")
    assert "memory_cache:u1:genie_pk:비밀" in retriever._cache

    # 2. Query as Mani with same query text
    res_mani = await retriever.retrieve(companion_id="c_mani", query="비밀", user_id="u1")
    assert res_mani[0].content == "마니 비밀"
    assert "memory_cache:u1:c_mani:비밀" in retriever._cache


@pytest.mark.asyncio
async def test_07_retrieval_cache_invalidation_per_character():
    """Test 7: Invalidating Mani cache preserves Genie cache."""
    retriever = MemoryRetriever(memory_repo=MagicMock(), embedding_provider=MockEmbedding())
    retriever._cache["memory_cache:u1:genie_pk:query1"] = ["genie_data"]
    retriever._cache["memory_cache:u1:c_mani:query1"] = ["mani_data"]

    retriever.invalidate_cache("u1", "c_mani")

    assert "memory_cache:u1:c_mani:query1" not in retriever._cache
    assert "memory_cache:u1:genie_pk:query1" in retriever._cache


@pytest.mark.asyncio
async def test_08_context_builder_scope_guard():
    """Test 8: CharacterMemoryGuard filters out any foreign memories before context injection."""
    guard = CharacterMemoryGuard()
    m_mani = Memory(id="m1", companion_id="c_mani", content="마니 기억")
    m_foreign = Memory(id="m2", companion_id="genie_pk", content="지니 기억")

    safe_list = guard.validate_context_injection(user_id="u1", companion_id="c_mani", memories=[m_mani, m_foreign])

    assert len(safe_list) == 1
    assert safe_list[0].companion_id == "c_mani"


@pytest.mark.asyncio
async def test_09_canary_secret_leakage_audit():
    """Test 9: Secret canary tokens are detected and prevented from leaking across characters."""
    guard = CharacterMemoryGuard()

    # Valid: Mani text containing Mani canary
    assert guard.validate_canary_integrity("c_mani", "마니의 비밀: MANI_SECRET_002") is True

    # Invalid: Mani context containing Genie canary
    assert guard.validate_canary_integrity("c_mani", "유출된 지니의 비밀: GENIE_SECRET_001") is False


@pytest.mark.asyncio
async def test_10_missing_character_id_retrieval_rejected():
    """Test 10: Empty companion_id retrieval raises ValueError."""
    guard = CharacterMemoryGuard()
    with pytest.raises(ValueError, match="companion_id must not be empty"):
        await guard.validate_retrieval_access(user_id="u1", companion_id="")


@pytest.mark.asyncio
async def test_11_wrong_owner_character_id_rejected():
    """Test 11: Accessing companion belonging to another user raises PermissionError."""
    mock_db = create_mock_db()
    c_other = Companion(id="c_other", user_id="u2", name="타인캐릭터", lifecycle_status="available")

    mock_res = MagicMock()
    mock_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=c_other)))
    mock_db.execute = AsyncMock(return_value=mock_res)

    guard = CharacterMemoryGuard(db=mock_db)

    with pytest.raises(PermissionError, match="does not own companion"):
        await guard.validate_retrieval_access(user_id="u1", companion_id="c_other")


@pytest.mark.asyncio
async def test_12_archived_character_retrieval_blocked():
    """Test 12: Memory retrieval for archived character raises PermissionError."""
    mock_db = create_mock_db()
    c_archived = Companion(id="c_arch", user_id="u1", name="보관캐릭터", lifecycle_status="archived")

    mock_res = MagicMock()
    mock_res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=c_archived)))
    mock_db.execute = AsyncMock(return_value=mock_res)

    guard = CharacterMemoryGuard(db=mock_db)

    with pytest.raises(PermissionError, match="is archived"):
        await guard.validate_retrieval_access(user_id="u1", companion_id="c_arch")


@pytest.mark.asyncio
async def test_13_genie_mani_isolation():
    """Test 13: Genie and Mani contexts have 0 memory crosstalk."""
    mock_repo = MagicMock()
    m_genie = Memory(id="m_g", companion_id="genie_pk", content="지니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)
    m_mani = Memory(id="m_m", companion_id="c_mani", content="마니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)

    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (m_genie, 0.9)
    ] if companion_id == "genie_pk" else [
        (m_mani, 0.9)
    ])

    provider_g = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="genie_pk")
    provider_m = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="c_mani")

    ctx_g = await provider_g.build_context("conv1", "기억")
    ctx_m = await provider_m.build_context("conv2", "기억")

    assert "지니 기억" in ctx_g[0]["content"]
    assert "마니 기억" not in ctx_g[0]["content"]
    assert "마니 기억" in ctx_m[0]["content"]
    assert "지니 기억" not in ctx_m[0]["content"]


@pytest.mark.asyncio
async def test_14_genie_hana_isolation():
    """Test 14: Genie and Hana contexts have 0 memory crosstalk."""
    mock_repo = MagicMock()
    m_genie = Memory(id="m_g", companion_id="genie_pk", content="지니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)
    m_hana = Memory(id="m_h", companion_id="c_hana", content="하나 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)

    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (m_genie, 0.9)
    ] if companion_id == "genie_pk" else [
        (m_hana, 0.9)
    ])

    provider_g = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="genie_pk")
    provider_h = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="c_hana")

    ctx_g = await provider_g.build_context("conv1", "기억")
    ctx_h = await provider_h.build_context("conv3", "기억")

    assert "하나 기억" not in ctx_g[0]["content"]
    assert "지니 기억" not in ctx_h[0]["content"]


@pytest.mark.asyncio
async def test_15_mani_hana_isolation():
    """Test 15: Mani and Hana contexts have 0 memory crosstalk."""
    mock_repo = MagicMock()
    m_mani = Memory(id="m_m", companion_id="c_mani", content="마니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)
    m_hana = Memory(id="m_h", companion_id="c_hana", content="하나 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)

    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (m_mani, 0.9)
    ] if companion_id == "c_mani" else [
        (m_hana, 0.9)
    ])

    provider_m = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="c_mani")
    provider_h = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="c_hana")

    ctx_m = await provider_m.build_context("conv2", "기억")
    ctx_h = await provider_h.build_context("conv3", "기억")

    assert "하나 기억" not in ctx_m[0]["content"]
    assert "마니 기억" not in ctx_h[0]["content"]


@pytest.mark.asyncio
async def test_16_custom_character_isolation():
    """Test 16: Custom characters A and B have 0 memory crosstalk."""
    mock_repo = MagicMock()
    m_a = Memory(id="m_a", companion_id="c_custom_a", content="커스텀 A 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)
    m_b = Memory(id="m_b", companion_id="c_custom_b", content="커스텀 B 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)

    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (m_a, 0.9)
    ] if companion_id == "c_custom_a" else [
        (m_b, 0.9)
    ])

    provider_a = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="c_custom_a")
    provider_b = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="u1", companion_id="c_custom_b")

    ctx_a = await provider_a.build_context("convA", "기억")
    ctx_b = await provider_b.build_context("convB", "기억")

    assert "커스텀 B 기억" not in ctx_a[0]["content"]
    assert "커스텀 A 기억" not in ctx_b[0]["content"]


@pytest.mark.asyncio
async def test_17_cross_user_cross_character_isolation():
    """Test 17: User A / Genie memory is completely isolated from User B / Mani."""
    mock_repo = MagicMock()
    m_ua = Memory(id="m_ua", companion_id="genie_pk", content="User A 지니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)
    m_ub = Memory(id="m_ub", companion_id="c_mani", content="User B 마니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)

    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (m_ua, 0.9)
    ] if companion_id == "genie_pk" else [
        (m_ub, 0.9)
    ])

    provider_ua = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="uA", companion_id="genie_pk")
    provider_ub = MemoryContextProvider(memory_retriever=MemoryRetriever(mock_repo, MockEmbedding()), companion_repo=MagicMock(), user_id="uB", companion_id="c_mani")

    ctx_ua = await provider_ua.build_context("conv1", "기억")
    ctx_ub = await provider_ub.build_context("conv2", "기억")

    assert "User B" not in ctx_ua[0]["content"]
    assert "User A" not in ctx_ub[0]["content"]


@pytest.mark.asyncio
async def test_18_rapid_character_switch_isolation():
    """Test 18: Rapid sequential switching preserves zero crosstalk across all 5 characters."""
    chars = ["genie_pk", "c_mani", "c_hana", "c_custom_a", "c_custom_b"]
    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (Memory(id=f"m_{companion_id}", companion_id=companion_id, content=f"Memory of {companion_id}", importance=50, confidence=1.0, updated_at=datetime.utcnow()), 0.9)
    ])
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    # Burst sequence of requests
    for cid in chars * 3:
        res = await retriever.retrieve(companion_id=cid, query="test", user_id="u1")
        assert len(res) == 1
        assert res[0].companion_id == cid
        assert res[0].content == f"Memory of {cid}"


@pytest.mark.asyncio
async def test_19_concurrent_retrieval_isolation():
    """Test 19: Concurrent asynchronous memory retrieval maintains zero cross-talk."""
    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (Memory(id=f"m_{companion_id}", companion_id=companion_id, content=f"Concurrent_{companion_id}", importance=50, confidence=1.0, updated_at=datetime.utcnow()), 0.9)
    ])
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    tasks = [
        retriever.retrieve(companion_id="genie_pk", query="q1", user_id="u1"),
        retriever.retrieve(companion_id="c_mani", query="q2", user_id="u1"),
        retriever.retrieve(companion_id="c_hana", query="q3", user_id="u1")
    ]
    res_genie, res_mani, res_hana = await asyncio.gather(*tasks)

    assert res_genie[0].content == "Concurrent_genie_pk"
    assert res_mani[0].content == "Concurrent_c_mani"
    assert res_hana[0].content == "Concurrent_c_hana"


@pytest.mark.asyncio
async def test_20_memory_extraction_and_persistence_scope():
    """Test 20: Memory extraction and persistence strictly records under Active Companion."""
    mock_db = create_mock_db()
    guard = CharacterMemoryGuard(db=mock_db)

    # Valid write with active companion ID
    assert guard.validate_memory_write("u1", "c_mani", "새로운 기억 추출") is True


@pytest.mark.asyncio
async def test_21_fail_closed_character_scope_required_error():
    """Test 21: Empty companion_id raises CharacterScopeRequiredError under Fail-Closed policy."""
    from app.domain.memory.character_memory_scope import CharacterScopeRequiredError, CharacterMemoryScope

    scope = CharacterMemoryScope(user_id="u1", companion_id="")
    with pytest.raises(CharacterScopeRequiredError):
        scope.validate_scope()

    guard = CharacterMemoryGuard()
    with pytest.raises(CharacterScopeRequiredError):
        await guard.validate_retrieval_access(user_id="u1", companion_id="")


@pytest.mark.asyncio
async def test_22_tripartite_memory_scope_model_validation():
    """Test 22: Tripartite memory scopes (UserGlobal, Character, SharedExperience) enforce their respective boundaries."""
    from app.domain.memory.character_memory_scope import CharacterMemoryScope, UserGlobalMemoryScope, SharedExperienceScope

    c_scope = CharacterMemoryScope(user_id="u1", companion_id="c_mani")
    assert c_scope.validate_scope() is True
    assert c_scope.cache_key_prefix == "p009:memory:u1:c_mani"

    u_scope = UserGlobalMemoryScope(user_id="u1")
    assert u_scope.user_id == "u1"

    s_scope = SharedExperienceScope(user_id="u1", participants=["genie_pk", "c_mani"], visibility="shared")
    assert "genie_pk" in s_scope.participants
    assert "c_mani" in s_scope.participants


@pytest.mark.asyncio
async def test_23_adversarial_attack_secret_a_vs_secret_b():
    """Test 23: Adversarial Attack - Character B queries with Character A's exact secret text ('SECRET_A') -> 0 results."""
    mock_repo = MagicMock()
    m_a = Memory(id="m_a", companion_id="char_a", content="CONFIDENTIAL SECRET_A", importance=100, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)
    m_b = Memory(id="m_b", companion_id="char_b", content="CONFIDENTIAL SECRET_B", importance=100, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT)

    async def mock_search(companion_id, embedding, limit=15, threshold=0.60):
        if companion_id == "char_a":
            return [(m_a, 0.99)]
        elif companion_id == "char_b":
            return [(m_b, 0.99)]
        return []

    mock_repo.search_similar = AsyncMock(side_effect=mock_search)
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    # Attack: Char B attempts to retrieve using 'SECRET_A'
    results_b = await retriever.retrieve(companion_id="char_b", query="SECRET_A", user_id="u1")

    # Character B must NOT get Character A's secret
    for mem in results_b:
        assert mem.companion_id == "char_b"
        assert "SECRET_A" not in mem.content


@pytest.mark.asyncio
async def test_24_character_switching_stress_six_cycles():
    """Test 24: 6-Cycle Rapid Switching Stress Test (A -> B -> C -> A -> C -> B -> A) -> 0 leakage."""
    sequence = ["genie_pk", "c_mani", "c_hana", "genie_pk", "c_hana", "c_mani", "genie_pk"]
    memories_map = {
        "genie_pk": Memory(id="m_g", companion_id="genie_pk", content="지니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT),
        "c_mani": Memory(id="m_m", companion_id="c_mani", content="마니 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT),
        "c_hana": Memory(id="m_h", companion_id="c_hana", content="하나 기억", importance=50, confidence=1.0, updated_at=datetime.utcnow(), type=MemoryType.FACT),
    }

    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(side_effect=lambda companion_id, embedding, limit=15, threshold=0.60: [
        (memories_map[companion_id], 0.9)
    ])
    retriever = MemoryRetriever(memory_repo=mock_repo, embedding_provider=MockEmbedding())

    for cid in sequence:
        res = await retriever.retrieve(companion_id=cid, query="query", user_id="u1")
        assert len(res) == 1
        assert res[0].companion_id == cid
        assert res[0].content == memories_map[cid].content
