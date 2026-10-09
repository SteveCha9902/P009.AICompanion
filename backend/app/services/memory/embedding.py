from abc import ABC, abstractmethod
from typing import List
import os
import openai
import logging

logger = logging.getLogger(__name__)

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class MockEmbeddingProvider(BaseEmbeddingProvider):
    async def embed(self, text: str) -> List[float]:
        return [0.0] * 1536

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * 1536 for _ in texts]

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        self.model = model
        key = api_key or os.getenv("OPENAI_API_KEY") or "mock_key_for_dev_mode"
        self.client = openai.AsyncOpenAI(api_key=key)

    async def embed(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise e

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Failed to create batch embeddings: {e}")
            raise e
