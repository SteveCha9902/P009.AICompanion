import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.context.builder import ContextBuilder
from app.services.context.providers.memory_provider import MemoryContextProvider
from app.services.memory.retriever import MemoryRetriever
from app.db.models.memory import Memory, MemoryType, MemorySource

@pytest.mark.asyncio
async def test_memory_continuity_cross_session():
    # 1. Fact Memory stored in DB
    fact_memory = Memory(
        id="mem-001",
        companion_id="comp_1",
        type=MemoryType.PERSONAL_FACT,
        source=MemorySource.USER_EXPLICIT,
        content="사용자의 이름은 철수이다.",
        importance=90
    )
    
    # Mock Memory Retriever & Companion Repo
    retriever = MemoryRetriever(memory_repo=MagicMock(), embedding_provider=MagicMock())
    retriever.retrieve = AsyncMock(return_value=[fact_memory])

    mock_companion_repo = MagicMock()
    mock_companion_repo.get_by_user_id = AsyncMock(return_value=MagicMock(id="comp_1"))

    memory_provider = MemoryContextProvider(
        memory_retriever=retriever, 
        companion_repo=mock_companion_repo, 
        user_id="user_chulsoo"
    )
    builder = ContextBuilder(providers=[memory_provider])

    # 2. Session 1: User asks for name
    context_session_1 = await builder.build(
        conversation_id="conv_session_1", 
        current_user_message="내 이름이 뭐야?",
        companion_id="comp_1"
    )
    app_ctx_1 = context_session_1[1]["content"]
    assert "[MEMORY CONTEXT]" in app_ctx_1
    assert "사용자의 이름은 철수이다." in app_ctx_1

    # 3. Session 2 (App restart / New Session): Same user, new conversation_id
    context_session_2 = await builder.build(
        conversation_id="conv_session_2_after_restart", 
        current_user_message="내가 누구라고 했지?",
        companion_id="comp_1"
    )
    app_ctx_2 = context_session_2[1]["content"]
    assert "[MEMORY CONTEXT]" in app_ctx_2
    assert "사용자의 이름은 철수이다." in app_ctx_2
