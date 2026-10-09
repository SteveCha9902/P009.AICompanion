import logging
import uuid
import asyncio
from typing import Optional, Any, List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.domain.character.update_request import CharacterUpdateRequest
from app.domain.character.character_summary import CharacterSummary
from app.domain.character.change_classification import ChangeType, CharacterChangeClassifier
from app.domain.character.lifecycle_status import CharacterLifecycleStatus
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.template_registry import CharacterTemplateRegistry
from app.services.character.personality_compiler import PersonalityCompiler
from app.services.character.context_resolver import CharacterContextResolver

# DB Models
from app.db.models.companion import Companion
from app.db.models.character_profile import CharacterProfileModel
from app.db.models.character_personality import CharacterPersonalityModel
from app.db.models.character_version import CharacterVersionModel
from app.db.models.avatar import AvatarProfile

logger = logging.getLogger(__name__)


class CharacterLifecycleService:
    """
    Service managing Character Lifecycle transitions:
    - Update & Personality Evolution Versioning (Version 1 -> V2 MINOR/MAJOR)
    - Archival & Restoration
    - Soft Deletion
    - Active / System Character Protection
    - Runtime Context Cache Invalidation
    """

    def __init__(
        self,
        db_session: Any,
        registry_repo: Optional[CharacterRegistryRepository] = None,
        registry_service: Optional[CharacterRegistryService] = None,
        context_resolver: Optional[CharacterContextResolver] = None
    ):
        self.db = db_session
        self.registry_repo = registry_repo or CharacterRegistryRepository(db_session)
        self.registry_service = registry_service or CharacterRegistryService(self.registry_repo, db_session)
        self.context_resolver = context_resolver or CharacterContextResolver(db_session, self.registry_service)

    async def _get_companion_for_user(self, user_id: str, companion_id: str) -> Companion:
        """Validates ownership and retrieves companion entity."""
        companion = await self.registry_repo.get_owned_companion(user_id, companion_id)
        if not companion:
            raise PermissionError(f"User '{user_id}' does not have access to companion '{companion_id}'")
        return companion

    async def update_character(self, user_id: str, companion_id: str, request: CharacterUpdateRequest) -> CharacterSummary:
        """
        Evolves character configuration, generates version snapshot if personality/values change,
        invalidates runtime resolver cache, and preserves all accumulated cognitive memories.
        """
        companion = await self._get_companion_for_user(user_id, companion_id)
        if companion.lifecycle_status == CharacterLifecycleStatus.DELETED.value:
            raise ValueError(f"Cannot update deleted companion '{companion_id}'")

        # 1. Fetch current personality or create baseline
        current_mbti = "INFJ"
        pers_entity = None
        if hasattr(self.db, "execute"):
            stmt = select(CharacterPersonalityModel).filter(CharacterPersonalityModel.companion_id == companion_id)
            res = await self.db.execute(stmt)
            pers_entity = res.scalars().first()
            if pers_entity and pers_entity.mbti_type:
                current_mbti = pers_entity.mbti_type

        # 2. Classify Change Severity (COSMETIC vs MINOR vs MAJOR)
        change_type = CharacterChangeClassifier.classify(
            current_mbti=current_mbti,
            new_mbti=request.mbti,
            new_role_title=request.role_title,
            new_keywords=request.personality_keywords,
            new_speaking_style=request.speaking_style,
            new_voice_id=request.voice_id,
            new_avatar_preset=request.avatar_preset
        )

        # 3. Compile updated personality if relevant
        target_template = CharacterTemplateRegistry.get_template("custom")
        compiled_pers = PersonalityCompiler.compile(
            template=target_template,
            mbti=request.mbti or current_mbti,
            keywords=request.personality_keywords
        )

        # 4. Update Personality in DB
        if pers_entity:
            pers_entity.mbti_type = compiled_pers.mbti_type
            pers_entity.openness = compiled_pers.openness
            pers_entity.conscientiousness = compiled_pers.conscientiousness
            pers_entity.extraversion = compiled_pers.extraversion
            pers_entity.agreeableness = compiled_pers.agreeableness
            pers_entity.neuroticism = compiled_pers.neuroticism
            pers_entity.humor_level = compiled_pers.humor_level
            pers_entity.curiosity_level = compiled_pers.curiosity_level
            pers_entity.empathy_level = compiled_pers.empathy_level
            pers_entity.assertiveness = compiled_pers.assertiveness
            pers_entity.playfulness = compiled_pers.playfulness
            pers_entity.emotional_expressiveness = compiled_pers.emotional_expressiveness
            pers_entity.communication_directness = compiled_pers.communication_directness
            pers_entity.warmth = compiled_pers.warmth
            pers_entity.intellectuality = compiled_pers.intellectuality

        # 5. Update Profile
        if hasattr(self.db, "execute"):
            stmt_p = select(CharacterProfileModel).filter(CharacterProfileModel.companion_id == companion_id)
            res_p = await self.db.execute(stmt_p)
            prof = res_p.scalars().first()
            if prof:
                if request.role_title:
                    prof.self_description = f"{companion.name} ({request.role_title})"
                if request.origin_story:
                    prof.origin_story = request.origin_story

        # 6. Update Avatar Profile
        if request.avatar_preset and hasattr(self.db, "execute"):
            stmt_a = select(AvatarProfile).filter(AvatarProfile.companion_id == companion_id)
            res_a = await self.db.execute(stmt_a)
            av = res_a.scalars().first()
            if av:
                av.visual_style = request.avatar_preset

        # 7. Record Version Snapshot ONLY for MINOR and MAJOR changes (Cosmetic does not bump version)
        if change_type in [ChangeType.MINOR, ChangeType.MAJOR]:
            version_snapshot = {
                "identity": {
                    "name": companion.name,
                    "role_title": request.role_title or "AI Companion",
                    "origin_story": request.origin_story
                },
                "personality": {
                    "mbti": compiled_pers.mbti_type,
                    "openness": compiled_pers.openness,
                    "conscientiousness": compiled_pers.conscientiousness,
                    "extraversion": compiled_pers.extraversion,
                    "agreeableness": compiled_pers.agreeableness,
                    "neuroticism": compiled_pers.neuroticism,
                    "warmth": compiled_pers.warmth,
                    "assertiveness": compiled_pers.assertiveness,
                    "intellectuality": compiled_pers.intellectuality
                },
                "speech_principles": {
                    "speaking_style": request.speaking_style or "friendly_natural",
                    "voice_id": request.voice_id or "default_voice"
                },
                "avatar_preset": request.avatar_preset or "default_avatar"
            }

            v_num = 2
            if hasattr(self.db, "execute"):
                stmt_v = select(func.max(CharacterVersionModel.version)).filter(CharacterVersionModel.companion_id == companion_id)
                res_v = await self.db.execute(stmt_v)
                max_v = res_v.scalar()
                if max_v is not None:
                    v_num = max_v + 1

            version_record = CharacterVersionModel(
                companion_id=companion_id,
                version=v_num,
                dna_snapshot=version_snapshot,
                change_type=change_type.value
            )
            if hasattr(self.db, "add"):
                self.db.add(version_record)

        # 8. Commit Transaction
        await self._commit_session()

        # 9. Runtime Context & Active Cache Invalidation
        self.registry_service.invalidate_active_cache(user_id)
        if self.context_resolver:
            self.context_resolver.invalidate(user_id, companion_id)

        active_id = await self.registry_service.get_active_companion_id(user_id)
        return CharacterSummary(
            companion_id=companion.id,
            name=companion.name,
            role_title=request.role_title or "AI Companion",
            avatar_preview=f"assets/avatars/{companion.name.lower()}_default.png",
            voice_name=request.voice_id or f"{companion.name.lower()}_voice_v1",
            is_active=(companion.id == active_id)
        )

    async def archive_character(self, user_id: str, companion_id: str) -> CharacterSummary:
        """
        Archives a companion character.
        Fails with PermissionError if companion is system character.
        Fails with ValueError if companion is currently active.
        """
        companion = await self._get_companion_for_user(user_id, companion_id)

        # 1. System Character Protection
        if companion.is_system_character or "genie" in companion.id.lower() or companion.name == "지니":
            raise PermissionError("System default character (Genie) cannot be archived.")

        # 2. Active Character Protection
        active_id = await self.registry_service.get_active_companion_id(user_id)
        if active_id == companion.id:
            raise ValueError("Active character cannot be archived. Please switch to another companion first.")

        companion.lifecycle_status = CharacterLifecycleStatus.ARCHIVED.value
        companion.archived_at = datetime.utcnow()

        await self._commit_session()
        self.registry_service.invalidate_active_cache(user_id)
        if self.context_resolver:
            self.context_resolver.invalidate(user_id, companion_id)

        return CharacterSummary(
            companion_id=companion.id,
            name=companion.name,
            role_title="Archived Companion",
            avatar_preview=f"assets/avatars/{companion.name.lower()}_default.png",
            voice_name=f"{companion.name.lower()}_voice_v1",
            is_active=False
        )

    async def restore_character(self, user_id: str, companion_id: str) -> CharacterSummary:
        """
        Restores an archived companion back to available status.
        Rejects restoration from deleted state.
        """
        companion = await self._get_companion_for_user(user_id, companion_id)
        if companion.lifecycle_status == CharacterLifecycleStatus.DELETED.value:
            raise ValueError(f"Cannot restore deleted companion '{companion_id}'")

        companion.lifecycle_status = CharacterLifecycleStatus.AVAILABLE.value
        companion.archived_at = None

        await self._commit_session()
        self.registry_service.invalidate_active_cache(user_id)
        if self.context_resolver:
            self.context_resolver.invalidate(user_id, companion_id)

        active_id = await self.registry_service.get_active_companion_id(user_id)
        return CharacterSummary(
            companion_id=companion.id,
            name=companion.name,
            role_title="AI Companion",
            avatar_preview=f"assets/avatars/{companion.name.lower()}_default.png",
            voice_name=f"{companion.name.lower()}_voice_v1",
            is_active=(companion.id == active_id)
        )

    async def delete_character(self, user_id: str, companion_id: str) -> CharacterSummary:
        """
        Soft deletes a companion character.
        Fails with PermissionError if companion is system character.
        Fails with ValueError if companion is currently active.
        """
        companion = await self._get_companion_for_user(user_id, companion_id)

        # 1. System Character Protection
        if companion.is_system_character or "genie" in companion.id.lower() or companion.name == "지니":
            raise PermissionError("System default character (Genie) cannot be deleted.")

        # 2. Active Character Protection
        active_id = await self.registry_service.get_active_companion_id(user_id)
        if active_id == companion.id:
            raise ValueError("Active character cannot be deleted. Please switch to another companion first.")

        companion.lifecycle_status = CharacterLifecycleStatus.DELETED.value
        companion.deleted_at = datetime.utcnow()

        await self._commit_session()
        self.registry_service.invalidate_active_cache(user_id)
        if self.context_resolver:
            self.context_resolver.invalidate(user_id, companion_id)

        return CharacterSummary(
            companion_id=companion.id,
            name=companion.name,
            role_title="Deleted Companion",
            avatar_preview=f"assets/avatars/{companion.name.lower()}_default.png",
            voice_name=f"{companion.name.lower()}_voice_v1",
            is_active=False
        )

    async def get_version_history(self, user_id: str, companion_id: str) -> List[Dict[str, Any]]:
        """Retrieves audit trail of character DNA versions."""
        await self._get_companion_for_user(user_id, companion_id)
        if hasattr(self.db, "execute"):
            stmt = select(CharacterVersionModel).filter(
                CharacterVersionModel.companion_id == companion_id
            ).order_by(CharacterVersionModel.version.asc())
            res = await self.db.execute(stmt)
            records = res.scalars().all()
            return [
                {
                    "version": r.version,
                    "change_type": r.change_type,
                    "dna_snapshot": r.dna_snapshot,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in records
            ]
        return []

    async def _commit_session(self):
        if hasattr(self.db, "commit"):
            if asyncio.iscoroutinefunction(self.db.commit):
                await self.db.commit()
            else:
                self.db.commit()
