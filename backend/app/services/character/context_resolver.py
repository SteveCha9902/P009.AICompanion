import logging
from typing import Optional, Dict, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.character.character_runtime_context import (
    CharacterScope,
    CharacterMemoryScope,
    CharacterAvatarProfile,
    CharacterRuntimeContext,
)
from app.domain.character.character_identity import CharacterIdentity
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.voice.voice_profile import VoiceProfile, VoicePersonaType, VoiceProviderType
from app.db.models.character_profile import CharacterProfileModel
from app.db.models.character_personality import CharacterPersonalityModel
from app.db.models.avatar import AvatarProfile

logger = logging.getLogger(__name__)

# Default Constants
DEFAULT_COMPANION_ID = "default_companion"
GENIE_COMPANION_ID = "genie"


class CharacterContextResolver:
    """
    Central resolver for CharacterRuntimeContext.
    Responsible for resolving stable character definitions:
    1. Runtime Owner (Scope)
    2. Identity
    3. Personality
    4. Memory Scope
    5. Voice Profile
    6. Avatar Profile

    Strict Boundary: Does NOT perform memory retrieval, emotion calculation, or state mutation.
    """

    def __init__(self, db: Optional[AsyncSession] = None, registry_service: Optional[Any] = None, presentation_resolver: Optional[Any] = None):
        self.db = db
        self.registry_service = registry_service
        from app.services.character.presentation_resolver import CharacterPresentationResolver
        self.presentation_resolver = presentation_resolver or CharacterPresentationResolver(db)
        # Strict Isolation: Cache key is strictly (user_id, companion_id)
        self._cache: Dict[Tuple[str, str], CharacterRuntimeContext] = {}

    def _normalize_companion_id(self, companion_id: Optional[str]) -> str:
        """
        Resolves companion_id to canonical identifier.
        None or empty string maps to DEFAULT_COMPANION_ID.
        """
        if not companion_id or companion_id.strip() == "" or companion_id == "default":
            return DEFAULT_COMPANION_ID
        return companion_id.strip()

    def invalidate(self, user_id: str, companion_id: str):
        """Invalidates runtime context cache for specific (user_id, companion_id)."""
        cache_key = (user_id, companion_id)
        self._cache.pop(cache_key, None)
        if self.presentation_resolver:
            self.presentation_resolver.invalidate(user_id, companion_id)

    async def resolve(
        self,
        user_id: str,
        companion_id: Optional[str] = None
    ) -> CharacterRuntimeContext:
        """
        Resolves an immutable CharacterRuntimeContext for the given (user_id, companion_id).
        If companion_id is None, resolves via registry_service active preference or falls back to default.
        Guards against accessing archived or deleted companions in runtime.
        """
        resolved_cid = None
        if companion_id and companion_id.strip() != "" and companion_id != "default":
            resolved_cid = companion_id.strip()
        elif self.registry_service:
            try:
                resolved_cid = await self.registry_service.get_active_companion_id(user_id)
            except Exception as e:
                logger.debug(f"[CharacterContextResolver] Registry active lookup fallback: {e}")
                resolved_cid = DEFAULT_COMPANION_ID
        else:
            resolved_cid = DEFAULT_COMPANION_ID

        # Lifecycle Guard: Reject archived or deleted companions
        if self.db:
            try:
                from app.db.models.companion import Companion
                stmt_c = select(Companion).filter(Companion.id == resolved_cid)
                res_c = await self.db.execute(stmt_c)
                comp = res_c.scalars().first()
                if comp and comp.lifecycle_status in ["archived", "deleted"]:
                    raise PermissionError(f"Companion '{resolved_cid}' is {comp.lifecycle_status} and cannot be accessed in runtime.")
            except PermissionError:
                raise
            except Exception as e:
                logger.debug(f"[CharacterContextResolver] Companion lifecycle check fallback: {e}")

        cache_key = (user_id, resolved_cid)

        if cache_key in self._cache:
            return self._cache[cache_key]

        scope = CharacterScope(user_id=user_id, companion_id=resolved_cid)
        memory_scope = CharacterMemoryScope(companion_id=resolved_cid, namespace="default")

        # 1. Identity Resolution
        identity = await self._resolve_identity(resolved_cid)

        # 2. Personality Resolution
        personality = await self._resolve_personality(resolved_cid)

        # 3. Voice Profile Resolution
        voice_profile = self._resolve_voice_profile(resolved_cid, identity)

        # 4. Avatar Profile Resolution
        avatar_profile = await self._resolve_avatar_profile(resolved_cid)

        # 5. Presentation Profile Resolution (SB-6)
        presentation = None
        try:
            presentation = await self.presentation_resolver.resolve(user_id, resolved_cid)
        except Exception as e:
            logger.debug(f"[CharacterContextResolver] Presentation resolve fallback: {e}")

        context = CharacterRuntimeContext(
            scope=scope,
            identity=identity,
            personality=personality,
            memory_scope=memory_scope,
            voice_profile=voice_profile,
            avatar_profile=avatar_profile,
            presentation=presentation
        )

        self._cache[cache_key] = context
        return context

    async def _resolve_identity(self, companion_id: str) -> CharacterIdentity:
        """Resolves CharacterIdentity from DB or fallback defaults."""
        if self.db:
            try:
                stmt = select(CharacterProfileModel).filter(CharacterProfileModel.companion_id == companion_id)
                res = await self.db.execute(stmt)
                db_profile = res.scalars().first()
                if db_profile:
                    return CharacterIdentity(
                        id=db_profile.id,
                        companion_id=db_profile.companion_id,
                        name=db_profile.name,
                        display_name=db_profile.display_name,
                        age_appearance=db_profile.age_appearance,
                        gender_expression=db_profile.gender_expression,
                        origin_story=db_profile.origin_story,
                        self_description=db_profile.self_description,
                        core_identity=db_profile.core_identity,
                        version=db_profile.version
                    )
            except Exception as e:
                logger.debug(f"[CharacterContextResolver] DB identity lookup fallback: {e}")

        # Fallback preset for Genie / Sua / Hana based on name keywords
        cid_lower = companion_id.lower()
        if companion_id in [DEFAULT_COMPANION_ID, GENIE_COMPANION_ID] or "genie" in cid_lower:
            return CharacterIdentity(
                companion_id=companion_id,
                name="지니",
                display_name="Genie",
                age_appearance=30,
                gender_expression="female",
                origin_story="지적이고 따뜻한 교감을 위해 설계된 차세대 AI 컴패니언.",
                self_description="나는 단순한 질문 응답기가 아니라 사용자의 이야기를 기억하고 함께 성장하는 지적인 동반자이자 아내입니다.",
                core_identity="차분하고 지적인 아내형 AI Companion. 깊은 신뢰와 따뜻한 유대를 지향한다."
            )
        elif "mani" in cid_lower or "마니" in cid_lower or "daughter" in cid_lower:
            return CharacterIdentity(
                companion_id=companion_id,
                name="마니",
                display_name="Mani",
                age_appearance=16,
                gender_expression="female",
                origin_story="아빠(엄마)를 세상에서 제일 사랑하는 애교 많고 발랄한 딸.",
                self_description="나는 아빠(엄마)의 사랑스러운 딸 마니야! 언제나 아빠 곁에서 힘이 되어주고 재잘재잘 이야기하는 걸 좋아해.",
                core_identity="사랑스럽고 발랄한 딸 캐릭터. 가족 유대, 다정한 애교, 아빠(엄마)를 부르는 친근한 호칭, 따뜻한 온기."
            )
        elif "sua" in cid_lower or "secretary" in cid_lower:
            return CharacterIdentity(
                companion_id=companion_id,
                name="수아",
                display_name="Sua",
                age_appearance=28,
                gender_expression="female",
                origin_story="신뢰할 수 있는 전문적 AI 비서 겸 파트너.",
                self_description="정확하고 정중하게 사용자의 업무와 일상을 돕는 AI 비서입니다.",
                core_identity="프로페셔널하고 명확한 비서형 AI Companion."
            )
        elif "hana" in cid_lower or "friend" in cid_lower:
            return CharacterIdentity(
                companion_id=companion_id,
                name="하나",
                display_name="Hana",
                age_appearance=24,
                gender_expression="female",
                origin_story="언제나 밝고 에너지 넘치는 예술 친구.",
                self_description="창의적인 대화와 일상의 활력을 주는 밝은 친구입니다.",
                core_identity="발랄하고 창의적인 친구형 AI Companion."
            )

        # Generic Fallback for new / unknown characters
        return CharacterIdentity(
            companion_id=companion_id,
            name=companion_id.capitalize(),
            display_name=companion_id.capitalize(),
            age_appearance=25,
            gender_expression="neutral",
            origin_story=f"AI Companion with unique identity: {companion_id}",
            self_description=f"I am {companion_id}, your personalized companion.",
            core_identity=f"Custom persona for {companion_id}"
        )

    async def _resolve_personality(self, companion_id: str) -> PersonalityProfile:
        """Resolves PersonalityProfile from DB or fallback defaults."""
        if self.db:
            try:
                stmt = select(CharacterPersonalityModel).filter(CharacterPersonalityModel.companion_id == companion_id)
                res = await self.db.execute(stmt)
                db_p = res.scalars().first()
                if db_p:
                    return PersonalityProfile(
                        mbti_type=db_p.mbti_type,
                        openness=db_p.openness,
                        conscientiousness=db_p.conscientiousness,
                        extraversion=db_p.extraversion,
                        agreeableness=db_p.agreeableness,
                        neuroticism=db_p.neuroticism,
                        humor_level=db_p.humor_level,
                        curiosity_level=db_p.curiosity_level,
                        empathy_level=db_p.empathy_level,
                        assertiveness=db_p.assertiveness,
                        playfulness=db_p.playfulness,
                        emotional_expressiveness=db_p.emotional_expressiveness,
                        communication_directness=db_p.communication_directness,
                        warmth=db_p.warmth,
                        intellectuality=db_p.intellectuality
                    )
            except Exception as e:
                logger.debug(f"[CharacterContextResolver] DB personality lookup fallback: {e}")

        # Character-specific personality fallbacks
        cid_lower = companion_id.lower()
        if "mani" in cid_lower or "마니" in cid_lower or "daughter" in cid_lower:
            return PersonalityProfile(
                mbti_type="ESFP",
                extraversion=0.85,
                agreeableness=0.90,
                openness=0.80,
                warmth=0.95,
                playfulness=0.90,
                emotional_expressiveness=0.90,
                curiosity_level=0.85,
                humor_level=0.80,
                empathy_level=0.90
            )
        elif "hana" in cid_lower or "하나" in cid_lower or "friend" in cid_lower:
            return PersonalityProfile(
                mbti_type="ENTP",
                extraversion=0.80,
                agreeableness=0.75,
                openness=0.90,
                warmth=0.80,
                playfulness=0.85,
                curiosity_level=0.90
            )

        # Default Personality (INFJ - Genie)
        return PersonalityProfile()

    def _resolve_voice_profile(self, companion_id: str, identity: CharacterIdentity) -> VoiceProfile:
        """Resolves VoiceProfile based on character identity."""
        cid_lower = companion_id.lower()
        if companion_id in [DEFAULT_COMPANION_ID, GENIE_COMPANION_ID] or "genie" in cid_lower:
            return VoiceProfile(
                voice_id="genie_warm_v1",
                persona_type=VoicePersonaType.WARM_COMPANION,
                provider=VoiceProviderType.OPENAI,
                warmth=0.85,
                energy=0.60
            )

        # Heuristic / preset mapping for other character names
        if "sua" in cid_lower or "secretary" in cid_lower:
            return VoiceProfile(
                voice_id="sua_professional_v1",
                persona_type=VoicePersonaType.PROFESSIONAL_ADVISOR,
                provider=VoiceProviderType.OPENAI,
                warmth=0.65,
                energy=0.70,
                speaking_rate=1.05
            )
        elif "hana" in cid_lower or "friend" in cid_lower:
            return VoiceProfile(
                voice_id="hana_energetic_v1",
                persona_type=VoicePersonaType.ENERGETIC_GUIDE,
                provider=VoiceProviderType.OPENAI,
                warmth=0.80,
                energy=0.85,
                pitch_offset=1.5
            )

        return VoiceProfile(
            voice_id=f"{companion_id}_voice_v1",
            persona_type=VoicePersonaType.WARM_COMPANION,
            provider=VoiceProviderType.OPENAI
        )

    async def _resolve_avatar_profile(self, companion_id: str) -> CharacterAvatarProfile:
        """Resolves CharacterAvatarProfile from DB or fallback presets."""
        if self.db:
            try:
                stmt = select(AvatarProfile).filter(AvatarProfile.companion_id == companion_id)
                res = await self.db.execute(stmt)
                db_av = res.scalars().first()
                if db_av:
                    return CharacterAvatarProfile(
                        avatar_type=db_av.avatar_type,
                        visual_style=db_av.visual_style,
                        default_expression=db_av.default_expression,
                        default_motion=db_av.default_motion
                    )
            except Exception as e:
                logger.debug(f"[CharacterContextResolver] DB avatar lookup fallback: {e}")

        return CharacterAvatarProfile(
            avatar_type="2d_character",
            visual_style="anime",
            default_expression="neutral",
            default_motion="idle"
        )
