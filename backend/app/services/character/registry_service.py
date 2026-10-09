import logging
from typing import Optional, List, Dict, Any

from app.domain.character.character_summary import CharacterSummary
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.db.models.companion import Companion
from app.db.models.character_profile import CharacterProfileModel

logger = logging.getLogger(__name__)

DEFAULT_GENIE_NAME = "지니"
DEFAULT_GENIE_ROLE = "AI Companion"


class CharacterRegistryService:
    """
    Business Domain Service for Multi-Character Registry & Active Companion Discovery.
    Handles:
    - Listing user's owned characters with summary metadata.
    - Lazy Bootstrap of active preference for legacy single-companion users.
    - Atomic ownership validation & active character switching.
    - Active Companion mapping cache invalidation.
    """

    def __init__(self, repository: CharacterRegistryRepository, db_session: Optional[Any] = None):
        self.repo = repository
        self.db = db_session or repository.db
        # In-memory fast cache for active companion lookup: {user_id: active_companion_id}
        self._active_companion_cache: Dict[str, str] = {}

    def invalidate_active_cache(self, user_id: str):
        """Invalidates active companion lookup cache for user_id."""
        self._active_companion_cache.pop(user_id, None)

    async def get_active_companion_id(self, user_id: str) -> str:
        """
        Retrieves active companion ID for user_id with Lazy Bootstrap.
        If no preference exists, automatically bootstraps with existing Genie companion.
        """
        if user_id in self._active_companion_cache:
            return self._active_companion_cache[user_id]

        # 1. Check existing preference
        pref = await self.repo.get_preference(user_id)
        if pref and pref.active_companion_id:
            self._active_companion_cache[user_id] = pref.active_companion_id
            return pref.active_companion_id

        # 2. Lazy Bootstrap: Find user's existing companion in DB
        owned_companions = await self.repo.list_by_user(user_id)
        if owned_companions:
            # Pick first or Genie
            target_companion = owned_companions[0]
            for c in owned_companions:
                if c.name == DEFAULT_GENIE_NAME or "genie" in c.id.lower():
                    target_companion = c
                    break
            
            # Bootstrap preference with existing Companion PK
            new_pref = await self.repo.set_active_companion(user_id, target_companion.id)
            self._active_companion_cache[user_id] = new_pref.active_companion_id
            return new_pref.active_companion_id

        # 3. Fallback for test / memory mode without DB companion records
        fallback_id = "default_companion"
        self._active_companion_cache[user_id] = fallback_id
        return fallback_id

    async def list_characters(self, user_id: str, include_archived: bool = False) -> List[CharacterSummary]:
        """
        Lists all characters owned by user_id with active status flags.
        By default, returns only AVAILABLE characters unless include_archived is True.
        """
        active_id = await self.get_active_companion_id(user_id)
        owned_companions = await self.repo.list_by_user(user_id, include_archived=include_archived)

        if not owned_companions:
            # If no DB records exist yet, return default Genie summary
            return [
                CharacterSummary(
                    companion_id=active_id,
                    name=DEFAULT_GENIE_NAME,
                    role_title=DEFAULT_GENIE_ROLE,
                    avatar_preview="assets/avatars/genie_default.png",
                    voice_name="genie_warm_v1",
                    is_active=True
                )
            ]

        summaries = []
        for comp in owned_companions:
            is_active = (comp.id == active_id)
            # Derive metadata or fallback
            role_title = DEFAULT_GENIE_ROLE
            if comp.name != DEFAULT_GENIE_NAME:
                role_title = f"AI {comp.name}"
            
            summaries.append(
                CharacterSummary(
                    companion_id=comp.id,
                    name=comp.name,
                    role_title=role_title,
                    avatar_preview=f"assets/avatars/{comp.name.lower()}_default.png",
                    voice_name=f"{comp.name.lower()}_voice_v1",
                    is_active=is_active
                )
            )

        return summaries

    async def validate_ownership(self, user_id: str, companion_id: str) -> bool:
        """Checks if companion_id is owned by user_id."""
        companion = await self.repo.get_owned_companion(user_id, companion_id)
        return companion is not None

    async def set_active_companion(self, user_id: str, companion_id: str) -> CharacterSummary:
        """
        Atomically validates ownership and switches user's active companion.
        Raises PermissionError if companion is not owned by user.
        Raises ValueError if companion is archived or deleted.
        """
        # 1. Atomic Ownership Validation
        companion = await self.repo.get_owned_companion(user_id, companion_id)
        if not companion:
            # Check if this is the default companion fallback
            if companion_id in ["default_companion", "genie"]:
                pass
            else:
                logger.warning(f"[RegistryService] Ownership check failed: user {user_id} does not own {companion_id}")
                raise PermissionError(f"User {user_id} does not have access to companion {companion_id}")

        if companion:
            # 2. Lifecycle Status Guard
            if companion.lifecycle_status in ["archived", "deleted"]:
                logger.warning(f"[RegistryService] Cannot activate {companion.lifecycle_status} companion {companion_id}")
                raise ValueError(f"Cannot activate {companion.lifecycle_status} character '{companion.name}'.")

        actual_companion_id = companion.id if companion else companion_id
        actual_name = companion.name if companion else (DEFAULT_GENIE_NAME if companion_id in ["default_companion", "genie"] else companion_id.capitalize())

        # 3. Update Preference in DB
        await self.repo.set_active_companion(user_id, actual_companion_id)

        # 4. Invalidate Active Cache
        self.invalidate_active_cache(user_id)
        self._active_companion_cache[user_id] = actual_companion_id

        return CharacterSummary(
            companion_id=actual_companion_id,
            name=actual_name,
            role_title=DEFAULT_GENIE_ROLE if actual_name == DEFAULT_GENIE_NAME else f"AI {actual_name}",
            avatar_preview=f"assets/avatars/{actual_name.lower()}_default.png",
            voice_name=f"{actual_name.lower()}_voice_v1",
            is_active=True
        )
