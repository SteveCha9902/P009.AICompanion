import logging
import asyncio
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.future import select

from app.domain.character.presentation_profile import (
    VoiceProfileConfig,
    AvatarProfileConfig,
    ExpressionProfileConfig,
    GestureProfileConfig,
    CharacterPresentationProfile,
    CharacterPresentationContext,
)
from app.db.models.companion import Companion
from app.db.models.character_presentation_profile import CharacterPresentationProfileModel
from app.repositories.character_registry_repository import CharacterRegistryRepository

logger = logging.getLogger(__name__)


class CharacterPresentationResolver:
    """
    Resolves, caches, and updates character-specific presentation identities
    (Voice + Avatar + Expression + Gesture) with strict multi-character isolation.
    """

    def __init__(self, db: Any = None, registry_repo: Optional[CharacterRegistryRepository] = None):
        self.db = db
        self.registry_repo = registry_repo or (CharacterRegistryRepository(db) if db else None)
        # Strict isolation: key = "presentation:{user_id}:{companion_id}"
        self._cache: Dict[str, CharacterPresentationContext] = {}

    def _get_cache_key(self, user_id: str, companion_id: str) -> str:
        return f"presentation:{user_id}:{companion_id}"

    def invalidate(self, user_id: str, companion_id: str):
        """Invalidates presentation cache for a specific character."""
        cache_key = self._get_cache_key(user_id, companion_id)
        self._cache.pop(cache_key, None)
        logger.debug(f"[PresentationResolver] Cache invalidated for '{cache_key}'")

    def _get_default_presentation_profile(self, companion_id: str, name: str = "") -> CharacterPresentationProfile:
        """Returns baseline presentation presets for standard characters."""
        lower_id = companion_id.lower()
        lower_name = name.lower()

        # 1. Mani - 사랑스러운 딸 (Lovely Daughter)
        if "mani" in lower_id or "마니" in lower_name:
            return CharacterPresentationProfile(
                companion_id=companion_id,
                voice=VoiceProfileConfig(
                    provider="OPENAI",
                    voice_id="shimmer",
                    persona_type="ENERGETIC_GUIDE",
                    speaking_rate=1.05,
                    pitch_offset=2.0,
                    warmth=0.90,
                    energy=0.85,
                    empathy=0.85
                ),
                avatar=AvatarProfileConfig(
                    avatar_id="mani_default",
                    visual_style="lovely_daughter_2d",
                    default_expression="happy",
                    default_motion="cheerful_bounce",
                    portrait_path="assets/avatar_characters/mani_v1_neutral.jpg"
                ),
                expression=ExpressionProfileConfig(
                    style="bright_cheerful",
                    gaze_style="curious_bright",
                    available_expressions=[
                        "happy", "sparkling_eyes", "defensive_pout", "embarrassed_blush", "secret_smile", "neutral", "surprised"
                    ]
                ),
                gesture=GestureProfileConfig(
                    style="playful_lively",
                    frequency="frequent",
                    available_gestures=[
                        "cheerful_bounce", "excited_wave", "small_hop", "curious_tilt", "arms_crossed_pout", "hiding_smile"
                    ]
                )
            )

        # 2. Hana - 취미 친구 (Hobby Friend)
        elif "hana" in lower_id or "하나" in lower_name:
            return CharacterPresentationProfile(
                companion_id=companion_id,
                voice=VoiceProfileConfig(
                    provider="OPENAI",
                    voice_id="alloy",
                    persona_type="WARM_COMPANION",
                    speaking_rate=1.00,
                    pitch_offset=0.5,
                    warmth=0.80,
                    energy=0.75,
                    empathy=0.75
                ),
                avatar=AvatarProfileConfig(
                    avatar_id="hana_default",
                    visual_style="casual_friend_2d",
                    default_expression="friendly",
                    default_motion="relaxed_idle"
                ),
                expression=ExpressionProfileConfig(
                    style="casual_playful",
                    gaze_style="direct_relaxed",
                    available_expressions=["friendly", "grin", "winking", "casual_nod", "neutral"]
                ),
                gesture=GestureProfileConfig(
                    style="expressive_casual",
                    frequency="natural",
                    available_gestures=["relaxed_idle", "thumb_up", "playful_point", "shoulder_shrug"]
                )
            )

        # 3. Genie / Default - 사랑스러운 아내 (Loving Wife)
        else:
            return CharacterPresentationProfile(
                companion_id=companion_id,
                voice=VoiceProfileConfig(
                    provider="OPENAI",
                    voice_id="nova",
                    persona_type="WARM_COMPANION",
                    speaking_rate=0.95,
                    pitch_offset=0.0,
                    warmth=0.95,
                    energy=0.60,
                    empathy=0.95
                ),
                avatar=AvatarProfileConfig(
                    avatar_id="genie_default",
                    visual_style="warm_wife_2d",
                    default_expression="affectionate",
                    default_motion="gentle_sway"
                ),
                expression=ExpressionProfileConfig(
                    style="warm_affectionate",
                    gaze_style="loving_eye_contact",
                    available_expressions=["affectionate", "gentle_smile", "caring_concern", "neutral", "thinking"]
                ),
                gesture=GestureProfileConfig(
                    style="soft_intimate",
                    frequency="natural",
                    available_gestures=["gentle_sway", "soft_wave", "close_hand_gesture", "gentle_nod"]
                )
            )

    async def resolve(self, user_id: str, companion_id: str) -> CharacterPresentationContext:
        """
        Resolves CharacterPresentationContext for the specified character.
        Validates SB-5 lifecycle status (rejects archived/deleted characters).
        """
        cache_key = self._get_cache_key(user_id, companion_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        companion_name = ""
        # 1. Lifecycle & Ownership Guard
        if self.db:
            try:
                stmt_c = select(Companion).filter(Companion.id == companion_id)
                res_c = await self.db.execute(stmt_c)
                comp = res_c.scalars().first()
                if comp:
                    companion_name = comp.name
                    if comp.lifecycle_status in ["archived", "deleted"]:
                        raise PermissionError(
                            f"Companion '{companion_id}' is {comp.lifecycle_status} and presentation runtime is blocked."
                        )
            except PermissionError:
                raise
            except Exception as e:
                logger.debug(f"[PresentationResolver] Lifecycle guard lookup fallback: {e}")

        # 2. Check DB Presentation Profile
        db_profile = None
        if self.db:
            try:
                stmt_p = select(CharacterPresentationProfileModel).filter(
                    CharacterPresentationProfileModel.companion_id == companion_id
                )
                res_p = await self.db.execute(stmt_p)
                db_profile = res_p.scalars().first()
            except Exception as e:
                logger.debug(f"[PresentationResolver] DB profile query fallback: {e}")

        # 3. Construct Presentation Context
        default_p = self._get_default_presentation_profile(companion_id, companion_name)
        if db_profile:
            vc = db_profile.voice_config or {}
            ac = db_profile.avatar_config or {}
            ec = db_profile.expression_config or {}
            gc = db_profile.gesture_config or {}

            voice = VoiceProfileConfig(
                provider=vc.get("provider", default_p.voice.provider),
                voice_id=vc.get("voice_id", default_p.voice.voice_id),
                persona_type=vc.get("persona_type", default_p.voice.persona_type),
                speaking_rate=float(vc.get("speaking_rate", default_p.voice.speaking_rate)),
                pitch_offset=float(vc.get("pitch_offset", default_p.voice.pitch_offset)),
                warmth=float(vc.get("warmth", default_p.voice.warmth)),
                energy=float(vc.get("energy", default_p.voice.energy)),
                empathy=float(vc.get("empathy", default_p.voice.empathy)),
            )
            avatar = AvatarProfileConfig(
                avatar_id=ac.get("avatar_id", default_p.avatar.avatar_id),
                visual_style=ac.get("visual_style", default_p.avatar.visual_style),
                default_expression=ac.get("default_expression", default_p.avatar.default_expression),
                default_motion=ac.get("default_motion", default_p.avatar.default_motion),
            )
            expression = ExpressionProfileConfig(
                style=ec.get("style", default_p.expression.style),
                gaze_style=ec.get("gaze_style", default_p.expression.gaze_style),
                available_expressions=ec.get("available_expressions", default_p.expression.available_expressions),
            )
            gesture = GestureProfileConfig(
                style=gc.get("style", default_p.gesture.style),
                frequency=gc.get("frequency", default_p.gesture.frequency),
                available_gestures=gc.get("available_gestures", default_p.gesture.available_gestures),
            )
        else:
            voice = default_p.voice
            avatar = default_p.avatar
            expression = default_p.expression
            gesture = default_p.gesture

        context = CharacterPresentationContext(
            companion_id=companion_id,
            voice=voice,
            avatar=avatar,
            expression=expression,
            gesture=gesture
        )

        self._cache[cache_key] = context
        return context

    async def update_presentation(
        self,
        user_id: str,
        companion_id: str,
        voice_updates: Optional[Dict[str, Any]] = None,
        avatar_updates: Optional[Dict[str, Any]] = None,
        expression_updates: Optional[Dict[str, Any]] = None,
        gesture_updates: Optional[Dict[str, Any]] = None
    ) -> CharacterPresentationContext:
        """
        Updates character presentation profile and invalidates cache.
        Validates ownership via registry_repo.
        """
        if self.registry_repo:
            owned = await self.registry_repo.get_owned_companion(user_id, companion_id)
            if not owned and companion_id not in ["default_companion", "genie"]:
                raise PermissionError(f"User '{user_id}' does not have access to companion '{companion_id}'")

        current = await self.resolve(user_id, companion_id)
        current_dict = current.to_dict()

        if voice_updates:
            current_dict["voice"].update(voice_updates)
        if avatar_updates:
            current_dict["avatar"].update(avatar_updates)
        if expression_updates:
            current_dict["expression"].update(expression_updates)
        if gesture_updates:
            current_dict["gesture"].update(gesture_updates)

        if self.db:
            stmt = select(CharacterPresentationProfileModel).filter(
                CharacterPresentationProfileModel.companion_id == companion_id
            )
            res = await self.db.execute(stmt)
            entity = res.scalars().first()
            if not entity:
                entity = CharacterPresentationProfileModel(
                    companion_id=companion_id,
                    voice_config=current_dict["voice"],
                    avatar_config=current_dict["avatar"],
                    expression_config=current_dict["expression"],
                    gesture_config=current_dict["gesture"]
                )
                if hasattr(self.db, "add"):
                    self.db.add(entity)
            else:
                entity.voice_config = current_dict["voice"]
                entity.avatar_config = current_dict["avatar"]
                entity.expression_config = current_dict["expression"]
                entity.gesture_config = current_dict["gesture"]

            if hasattr(self.db, "commit"):
                if asyncio.iscoroutinefunction(self.db.commit):
                    await self.db.commit()
                else:
                    self.db.commit()

        # Invalidate presentation cache
        self.invalidate(user_id, companion_id)
        return await self.resolve(user_id, companion_id)
