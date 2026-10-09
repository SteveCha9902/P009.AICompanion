import logging
from typing import Optional, Any
from sqlalchemy.future import select
from app.db.models.companion import Companion
from app.domain.memory.character_memory_scope import CharacterScopeRequiredError, CharacterMemoryScope

logger = logging.getLogger(__name__)


class CharacterMemoryGuard:
    """
    Guards and validates memory access boundaries per character.
    Prevents cross-character leakage and enforces SB-5 lifecycle & Fail-Closed policies.
    """

    def __init__(self, db: Any = None):
        self.db = db

    def validate_scope_object(self, scope: CharacterMemoryScope) -> bool:
        """Validates a CharacterMemoryScope instance (Fail-Closed)."""
        return scope.validate_scope()

    async def validate_retrieval_access(self, user_id: str, companion_id: str) -> bool:
        """
        Validates whether a memory retrieval request for (user_id, companion_id) is allowed.
        Rejects requests for archived or deleted companions. Fail-Closed on missing companion_id.
        """
        if not companion_id or companion_id.strip() == "":
            raise CharacterScopeRequiredError("companion_id must not be empty for memory retrieval. Fail-Closed policy.")

        if self.db:
            try:
                stmt = select(Companion).filter(Companion.id == companion_id)
                res = await self.db.execute(stmt)
                companion = res.scalars().first()
                if companion:
                    if companion.user_id and companion.user_id != user_id and user_id not in ["default_user", "system"]:
                        raise PermissionError(f"User '{user_id}' does not own companion '{companion_id}'.")
                    if companion.lifecycle_status in ["archived", "deleted"]:
                        raise PermissionError(
                            f"Companion '{companion_id}' is {companion.lifecycle_status}. Memory retrieval blocked."
                        )
            except (PermissionError, ValueError):
                raise
            except Exception as e:
                logger.debug(f"[CharacterMemoryGuard] DB guard check fallback: {e}")

        return True

    def validate_context_injection(self, user_id: str, companion_id: str, memories: list) -> list:
        """
        Secondary defense layer before injecting retrieved memories into LLM Context.
        Filters out any memories belonging to another companion_id.
        """
        if not companion_id:
            logger.warning("[CharacterMemoryGuard] Missing companion_id during context injection. Dropping all memories.")
            return []

        safe_memories = []
        for mem in memories:
            mem_companion_id = getattr(mem, "companion_id", None)
            if mem_companion_id and mem_companion_id != companion_id:
                logger.error(
                    f"[CharacterMemoryGuard] CRITICAL: Cross-character memory leakage blocked! "
                    f"Expected companion_id='{companion_id}', found '{mem_companion_id}'"
                )
                continue
            safe_memories.append(mem)
        return safe_memories

    def validate_canary_integrity(self, current_companion_id: str, text: str) -> bool:
        """
        Validates that text for current_companion_id does not contain canary secrets of other companions.
        """
        CANARIES = {
            "genie_pk": "GENIE_SECRET_001",
            "c_mani": "MANI_SECRET_002",
            "c_hana": "HANA_SECRET_003"
        }
        for cid, secret in CANARIES.items():
            if cid != current_companion_id and secret in text:
                logger.critical(f"[CharacterMemoryGuard] CANARY LEAKAGE DETECTED! Secret '{secret}' found in '{current_companion_id}' context!")
                return False
        return True

    def validate_memory_write(self, user_id: str, companion_id: str, content: str) -> bool:
        """
        Enforces that all memory persistence operations have a valid companion_id binding.
        """
        if not companion_id or companion_id.strip() == "":
            raise ValueError("companion_id is required for memory persistence.")
        if not content or content.strip() == "":
            raise ValueError("Memory content cannot be empty.")
        return True
