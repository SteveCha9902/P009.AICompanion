import time
from typing import List, Optional, Tuple
from app.domain.memory.relationship_memory import RelationshipMemory
from app.domain.awareness.awareness_context import AwarenessContext
from app.domain.shared_reality.shared_reality_context import SharedRealityContext
from app.services.memory.relationship.confidence_decay import ConfidenceDecayEngine

class MemoryVerificationLayer:
    """
    Guards against false memory hallucinations by validating confidence levels.
    """

    MIN_RECALL_CONFIDENCE = 0.50

    @classmethod
    def verify_recalled_memory(cls, memory: RelationshipMemory, effective_confidence: float) -> Tuple[bool, str]:
        """
        Returns (can_recall, recall_framing_style)
        - 'confident': Natural, direct recall ("전에 이야기했던 식물이네")
        - 'tentative': Soft, cautious recall ("내가 잘 기억하는지 모르겠지만...")
        - 'blocked': Low confidence, do not recall
        """
        if effective_confidence < cls.MIN_RECALL_CONFIDENCE:
            return (False, "blocked")
        elif effective_confidence < 0.70:
            return (True, "tentative")
        else:
            return (True, "confident")


class RecallRankingEngine:
    """
    Ranks recalled memories using a 4-Factor Product:
    RecallScore = Relevance × Recency × Importance × Confidence
    Returns Top 1~3 best-matching memories to prevent memory clutter.
    """

    @classmethod
    def rank_and_select_memories(
        cls,
        memories: List[RelationshipMemory],
        user_utterance: str,
        awareness_context: Optional[AwarenessContext] = None,
        shared_reality_context: Optional[SharedRealityContext] = None,
        top_k: int = 3
    ) -> List[Tuple[RelationshipMemory, float, str]]:
        """
        Returns list of (Memory, RecallScore, FramingStyle) sorted by RecallScore descending.
        """
        scored_candidates: List[Tuple[RelationshipMemory, float, str]] = []
        now_ms = int(time.time() * 1000)

        # Extract active visual tags from awareness/shared reality
        active_visual_tags: List[str] = []
        if awareness_context and awareness_context.is_fresh:
            for o in awareness_context.environment_state.detected_objects:
                active_visual_tags.append(o.type.value.upper())
        if shared_reality_context and shared_reality_context.focus_target:
            active_visual_tags.append(shared_reality_context.focus_target.value.upper())

        for mem in memories:
            if mem.is_expired:
                continue

            # 1. Relevance Score (Text keyword match + Visual tag match)
            relevance = 0.20 # baseline
            for word in user_utterance.split():
                if len(word) >= 2 and word in mem.summary:
                    relevance += 0.35
            
            # Visual tag match boost (e.g. Memory has 'PLANT' and camera detects 'PLANT')
            for tag in mem.visual_tags:
                base_tag = tag.split(":")[0].upper()
                if base_tag in active_visual_tags:
                    relevance += 0.50 # Strong visual anchor boost

            relevance = min(1.0, relevance)
            if relevance < 0.30:
                continue # Insufficient contextual relevance

            # 2. Recency Factor (Normalized 0.5 ~ 1.0)
            days_ago = (now_ms - mem.last_referenced_at_ms) / (1000.0 * 60 * 60 * 24)
            recency = max(0.50, 1.0 - (days_ago / 180.0))

            # 3. Importance Factor
            importance = mem.importance_score

            # 4. Effective Confidence Factor
            effective_conf = ConfidenceDecayEngine.calculate_effective_confidence(mem)

            # Verification Guard
            can_recall, framing = MemoryVerificationLayer.verify_recalled_memory(mem, effective_conf)
            if not can_recall:
                continue

            recall_score = round(relevance * recency * importance * effective_conf, 3)
            scored_candidates.append((mem, recall_score, framing))

        # Sort by recall score descending
        scored_candidates.sort(key=lambda item: item[1], reverse=True)
        return scored_candidates[:top_k]
