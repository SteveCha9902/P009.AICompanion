import pytest
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.db.models.memory import Memory
from app.services.memory.retriever import MemoryRetriever

@pytest.fixture
def mock_memory_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def mock_embedding_provider():
    provider = AsyncMock()
    provider.embed.return_value = [0.1] * 1536
    return provider

@pytest.mark.asyncio
async def test_memory_retriever_ranking(mock_memory_repo, mock_embedding_provider):
    retriever = MemoryRetriever(mock_memory_repo, mock_embedding_provider)
    
    # Create some mock memories
    now = datetime.now(timezone.utc)
    
    # 1. High similarity, low importance, old
    m1 = Memory(id="1", importance=10, confidence=1.0, updated_at=now - timedelta(days=60))
    # 2. Low similarity, high importance, new
    m2 = Memory(id="2", importance=100, confidence=1.0, updated_at=now)
    # 3. Medium everything
    m3 = Memory(id="3", importance=50, confidence=0.8, updated_at=now - timedelta(days=15))
    
    # Return (Memory, similarity)
    # Remember similarities will be: m1=0.9, m2=0.5, m3=0.7
    mock_memory_repo.search_similar.return_value = [
        (m1, 0.9),
        (m2, 0.5),
        (m3, 0.7)
    ]
    
    # Weights: sim=0.5, imp=0.2, rec=0.2, conf=0.1
    # m1 score = (0.9*0.5) + (0.1*0.2) + (0.25*0.2) + (1.0*0.1) = 0.45 + 0.02 + 0.05 + 0.1 = 0.62
    # m2 score = (0.5*0.5) + (1.0*0.2) + (1.0*0.2) + (1.0*0.1) = 0.25 + 0.2 + 0.2 + 0.1 = 0.75
    # m3 score ~ (0.7*0.5) + (0.5*0.2) + (0.7*0.2) + (0.8*0.1) = 0.35 + 0.1 + 0.14 + 0.08 = 0.67
    
    results = await retriever.retrieve("companion_id", "test query", top_k=3)
    
    # m2 should be ranked highest despite lower similarity because it's highly important and recent
    assert results[0].id == "2"
    assert results[1].id == "3"
    assert results[2].id == "1"
