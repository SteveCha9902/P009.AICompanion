from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.domain.memory.relationship_memory import RelationshipMemory
from app.services.memory.relationship.memory_store import RelationshipMemoryStore
from app.services.memory.relationship.candidate_extractor import CandidateExtractor
from app.services.memory.relationship.recall_engine import RecallRankingEngine
from app.services.memory.relationship.confidence_decay import ConfidenceDecayEngine
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator
from app.services.shared_reality.joint_attention_engine import JointAttentionEngine

class RelationshipMemoryCoordinator:
    """
    Coordinates extraction, storage, and recall of Relationship Memories.
    """

    @classmethod
    def process_and_extract_memory(cls, user_id: str, companion_id: str, utterance: str) -> Optional[RelationshipMemory]:
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        cand = CandidateExtractor.extract_candidate_memory(
            user_id=user_id,
            companion_id=companion_id,
            user_utterance=utterance,
            awareness_context=awareness_ctx
        )
        if cand:
            return RelationshipMemoryStore.save_memory(cand)
        return None

    @classmethod
    def recall_relevant_memories_guidance(cls, user_id: str, utterance: str) -> str:
        memories = RelationshipMemoryStore.list_user_memories(user_id)
        if not memories:
            return ""

        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        shared_reality_ctx = JointAttentionEngine.get_active_context()

        top_recalled = RecallRankingEngine.rank_and_select_memories(
            memories=memories,
            user_utterance=utterance,
            awareness_context=awareness_ctx,
            shared_reality_context=shared_reality_ctx,
            top_k=2
        )

        if not top_recalled:
            return ""

        guidance_lines = []
        for mem, score, framing in top_recalled:
            # Update reference count
            ConfidenceDecayEngine.update_on_reference(mem)

            if framing == "tentative":
                guidance_lines.append(
                    f"- [SOFT RECALLED MEMORY ({mem.memory_type.value})]: '{mem.summary}'. "
                    f"Frame tentatively (e.g. '내가 잘 기억하고 있는지 모르겠지만...'). DO NOT state with absolute certainty."
                )
            else:
                guidance_lines.append(
                    f"- [CONFIDENT RECALLED MEMORY ({mem.memory_type.value})]: '{mem.summary}'. "
                    f"Frame naturally as shared life context (e.g. '전에 이야기했던...', '지난번에 말씀하신...'). NEVER sound like an interrogator or surveillance database."
                )

        header = (
            "\n[PERSISTENT RELATIONSHIP MEMORY (Natural Companion Recall)]\n"
            "You have the following authentic shared memories with the user. "
            "Integrate them smoothly into conversation ONLY when relevant.\n"
        )
        return header + "\n".join(guidance_lines) + "\n"


class RelationshipMemoryContextProvider(ContextProvider):
    """
    5th Cognitive Layer: Relationship Memory Provider for ContextBuilder.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        # Auto-extract any new high-value memory from this turn
        RelationshipMemoryCoordinator.process_and_extract_memory(
            user_id=self.user_id,
            companion_id="default_companion",
            utterance=current_user_message
        )

        guidance = RelationshipMemoryCoordinator.recall_relevant_memories_guidance(
            user_id=self.user_id,
            utterance=current_user_message
        )
        if not guidance:
            return []
        return [{"role": "system", "content": guidance}]
