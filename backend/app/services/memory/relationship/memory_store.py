from typing import List, Optional, Dict
from app.domain.memory.relationship_memory import RelationshipMemory

class RelationshipMemoryStore:
    """
    In-Memory & Persistent storage for Relationship Memories.
    Enforces TTL Expiration and provides User Control (Review, Pin, Forget, Delete).
    """

    _memories: Dict[str, RelationshipMemory] = {} # memory_id -> memory

    @classmethod
    def save_memory(cls, memory: RelationshipMemory) -> RelationshipMemory:
        cls._memories[memory.id] = memory
        return memory

    @classmethod
    def get_memory(cls, memory_id: str) -> Optional[RelationshipMemory]:
        mem = cls._memories.get(memory_id)
        if mem and mem.is_expired:
            del cls._memories[memory_id]
            return None
        return mem

    @classmethod
    def list_user_memories(cls, user_id: str, include_expired: bool = False) -> List[RelationshipMemory]:
        """
        User Memory Center: Review all active memories.
        """
        active: List[RelationshipMemory] = []
        expired_ids: List[str] = []

        for m_id, m in cls._memories.items():
            if m.user_id == user_id:
                if m.is_expired and not include_expired:
                    expired_ids.append(m_id)
                else:
                    active.append(m)

        for e_id in expired_ids:
            del cls._memories[e_id]

        return active

    @classmethod
    def pin_memory(cls, memory_id: str, is_pinned: bool = True) -> bool:
        """
        User Control: Pin a memory so it never decays or expires.
        """
        mem = cls._memories.get(memory_id)
        if mem:
            mem.is_pinned = is_pinned
            return True
        return False

    @classmethod
    def delete_memory(cls, memory_id: str) -> bool:
        """
        User Control: Forget a specific memory.
        """
        if memory_id in cls._memories:
            del cls._memories[memory_id]
            return True
        return False

    @classmethod
    def forget_all_user_memories(cls, user_id: str) -> int:
        """
        User Control: Complete forget request for a user.
        """
        to_delete = [m_id for m_id, m in cls._memories.items() if m.user_id == user_id]
        for m_id in to_delete:
            del cls._memories[m_id]
        return len(to_delete)

    @classmethod
    def clear_all(cls) -> None:
        cls._memories.clear()
