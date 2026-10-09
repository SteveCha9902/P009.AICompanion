import time
from typing import List, Tuple, Optional, Any
from app.db.models.memory import Memory
from app.repositories.memory_repository import MemoryRepository
from app.services.memory.embedding import BaseEmbeddingProvider
import logging

logger = logging.getLogger(__name__)

class MemoryRetriever:
    def __init__(
        self,
        memory_repo: MemoryRepository,
        embedding_provider: BaseEmbeddingProvider,
        weights: dict = None,
        guard: Optional[Any] = None
    ):
        self.memory_repo = memory_repo
        self.embedding_provider = embedding_provider
        self.weights = weights or {
            "similarity": 0.50,
            "importance": 0.20,
            "recency": 0.20,
            "confidence": 0.10
        }
        from app.services.memory.character_memory_guard import CharacterMemoryGuard
        self.guard = guard or (CharacterMemoryGuard(getattr(memory_repo, "session", None)))
        # Strict isolation cache: key = "memory_cache:{user_id}:{companion_id}:{query}"
        self._cache: dict = {}

    def invalidate_cache(self, user_id: str, companion_id: str):
        """Invalidates memory retrieval cache for a specific character."""
        prefix = f"memory_cache:{user_id}:{companion_id}:"
        keys_to_del = [k for k in self._cache.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            self._cache.pop(k, None)

    def _calculate_recency_score(self, memory: Memory) -> float:
        """
        Calculate a score from 0.0 to 1.0 based on how recent the memory was created/updated.
        """
        if not memory.updated_at:
            return 0.0
            
        age_seconds = time.time() - memory.updated_at.timestamp()
        
        # Define half-life for memory decay (e.g., 30 days)
        half_life = 30 * 24 * 60 * 60
        score = 0.5 ** (age_seconds / half_life)
        return max(0.0, min(1.0, score))

    async def retrieve(
        self,
        companion_id: str,
        query: str,
        top_k: int = 5,
        user_id: Optional[str] = "default_user"
    ) -> List[Memory]:
        # 0. Character Scope & Lifecycle Validation
        if self.guard:
            await self.guard.validate_retrieval_access(user_id=user_id, companion_id=companion_id)

        cache_key = f"memory_cache:{user_id}:{companion_id}:{query.strip()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # 1. Embed query
            query_embedding = await self.embedding_provider.embed(query)
            
            # 2. Search similar active memories strictly scoped by companion_id
            similar_memories = await self.memory_repo.search_similar(
                companion_id=companion_id, 
                embedding=query_embedding, 
                limit=top_k * 3,
                threshold=0.60
            )

            # 3. Apply ranking formula
            ranked_results: List[Tuple[float, Memory]] = []
            for memory, similarity in similar_memories:
                importance_norm = memory.importance / 100.0
                recency_score = self._calculate_recency_score(memory)
                confidence = memory.confidence
                
                final_score = (
                    (similarity * self.weights["similarity"]) +
                    (importance_norm * self.weights["importance"]) +
                    (recency_score * self.weights["recency"]) +
                    (confidence * self.weights["confidence"])
                )
                ranked_results.append((final_score, memory))

            # 4. Sort by final score
            ranked_results.sort(key=lambda x: x[0], reverse=True)
            
            # Return Top K Memory objects
            results = [mem for score, mem in ranked_results[:top_k]]
            self._cache[cache_key] = results
            return results
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []
