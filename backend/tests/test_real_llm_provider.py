import pytest
import os
from unittest.mock import patch, MagicMock
from app.services.llm.openai import OpenAIProvider
from app.services.llm.base import LLMAuthError

@pytest.mark.asyncio
async def test_openai_provider_missing_key():
    with patch.dict(os.environ, {}, clear=True):
        provider = OpenAIProvider(api_key="")
        with pytest.raises(LLMAuthError, match="OPENAI_API_KEY is missing"):
            await provider.generate([{"role": "user", "content": "hello"}])

@pytest.mark.asyncio
async def test_openai_provider_stream_mocked():
    provider = OpenAIProvider(api_key="sk-test-key")
    
    # Mock AsyncOpenAI client
    mock_chunk_1 = MagicMock()
    mock_chunk_1.choices = [MagicMock(delta=MagicMock(content="안녕"), finish_reason=None)]
    mock_chunk_1.model = "gpt-4o-mini"
    
    mock_chunk_2 = MagicMock()
    mock_chunk_2.choices = [MagicMock(delta=MagicMock(content="하세요!"), finish_reason="stop")]
    mock_chunk_2.model = "gpt-4o-mini"

    class AsyncStreamMock:
        def __init__(self):
            self.items = [mock_chunk_1, mock_chunk_2]
            self.index = 0
            
        def __aiter__(self):
            return self
            
        async def __anext__(self):
            if self.index < len(self.items):
                item = self.items[self.index]
                self.index += 1
                return item
            raise StopAsyncIteration

    async def mock_create(*args, **kwargs):
        return AsyncStreamMock()

    with patch.object(provider.client.chat.completions, 'create', side_effect=mock_create):
        chunks = []
        async for chunk in provider.stream([{"role": "user", "content": "안녕"}]):
            chunks.append(chunk.content)
        
        assert "".join(chunks) == "안녕하세요!"
