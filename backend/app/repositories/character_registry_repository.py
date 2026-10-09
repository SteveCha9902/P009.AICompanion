import logging
import asyncio
from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models.companion import Companion
from app.db.models.user_character_preference import UserCharacterPreference

logger = logging.getLogger(__name__)


class CharacterRegistryRepository:
    """
    Data Access Layer for Multi-Character Registry and User Preferences.
    Supports both AsyncSession and Sync Session for compatibility.
    """

    def __init__(self, db: Any):
        self.db = db

    async def list_by_user(self, user_id: str, include_archived: bool = False, include_deleted: bool = False) -> List[Companion]:
        """Returns Companions owned by user_id, filtering by lifecycle_status."""
        allowed_statuses = ["available"]
        if include_archived:
            allowed_statuses.append("archived")
        if include_deleted:
            allowed_statuses.append("deleted")

        if hasattr(self.db, "execute"):
            stmt = select(Companion).filter(
                Companion.user_id == user_id,
                (Companion.lifecycle_status.in_(allowed_statuses) | Companion.lifecycle_status.is_(None))
            ).order_by(Companion.created_at.asc())
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        elif hasattr(self.db, "query"):
            return self.db.query(Companion).filter(
                Companion.user_id == user_id,
                (Companion.lifecycle_status.in_(allowed_statuses) | Companion.lifecycle_status.is_(None))
            ).order_by(Companion.created_at.asc()).all()
        return []

    async def get_owned_companion(self, user_id: str, companion_id: str) -> Optional[Companion]:
        """
        Validates ownership and retrieves companion within transaction.
        Checks if companion_id belongs to user_id.
        Also supports fallback matching for default/legacy companions where user_id matches.
        """
        if hasattr(self.db, "execute"):
            stmt = select(Companion).filter(Companion.id == companion_id, Companion.user_id == user_id)
            res = await self.db.execute(stmt)
            companion = res.scalars().first()
            if not companion:
                # Check by name or fallback if id has prefix
                stmt_fallback = select(Companion).filter(Companion.user_id == user_id)
                res_fb = await self.db.execute(stmt_fallback)
                all_c = res_fb.scalars().all()
                for c in all_c:
                    if c.id == companion_id or c.name.lower() == companion_id.lower():
                        return c
            return companion
        elif hasattr(self.db, "query"):
            c = self.db.query(Companion).filter(Companion.id == companion_id, Companion.user_id == user_id).first()
            if not c:
                all_c = self.db.query(Companion).filter(Companion.user_id == user_id).all()
                for comp in all_c:
                    if comp.id == companion_id or comp.name.lower() == companion_id.lower():
                        return comp
            return c
        return None

    async def get_preference(self, user_id: str) -> Optional[UserCharacterPreference]:
        """Retrieves UserCharacterPreference by user_id."""
        if hasattr(self.db, "execute"):
            stmt = select(UserCharacterPreference).filter(UserCharacterPreference.user_id == user_id)
            res = await self.db.execute(stmt)
            return res.scalars().first()
        elif hasattr(self.db, "query"):
            return self.db.query(UserCharacterPreference).filter(UserCharacterPreference.user_id == user_id).first()
        return None

    async def set_active_companion(self, user_id: str, companion_id: str) -> UserCharacterPreference:
        """
        Atomically creates or updates user's active companion preference.
        """
        pref = await self.get_preference(user_id)
        if pref:
            pref.active_companion_id = companion_id
            pref.updated_at = datetime.utcnow()
        else:
            pref = UserCharacterPreference(
                user_id=user_id,
                active_companion_id=companion_id
            )
            if hasattr(self.db, "add"):
                self.db.add(pref)

        if hasattr(self.db, "commit"):
            if asyncio.iscoroutinefunction(self.db.commit):
                await self.db.commit()
            else:
                self.db.commit()

        if hasattr(self.db, "refresh"):
            try:
                if asyncio.iscoroutinefunction(self.db.refresh):
                    await self.db.refresh(pref)
                else:
                    self.db.refresh(pref)
            except Exception:
                pass

        return pref
