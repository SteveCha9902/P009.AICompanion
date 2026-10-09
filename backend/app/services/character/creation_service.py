import logging
import uuid
import asyncio
from typing import Optional, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.domain.character.creation_request import CharacterCreationRequest
from app.domain.character.creation_result import CharacterCreationResult
from app.services.character.template_registry import CharacterTemplateRegistry
from app.services.character.personality_compiler import PersonalityCompiler
from app.services.character.character_factory import CharacterFactory
from app.services.character.creation_validator import (
    CharacterCreationValidator,
    CharacterValidationError,
    CharacterDuplicateNameError
)
from app.repositories.character_registry_repository import CharacterRegistryRepository

# DB Models
from app.db.models.companion import Companion
from app.db.models.character_profile import CharacterProfileModel
from app.db.models.character_personality import CharacterPersonalityModel
from app.db.models.character_value import CharacterValueModel
from app.db.models.character_version import CharacterVersionModel
from app.db.models.character_presentation_profile import CharacterPresentationProfileModel
from app.db.models.emotion import EmotionState, EmotionType
from app.db.models.relationship import RelationshipState, RelationshipLevel
from app.db.models.avatar import AvatarProfile

logger = logging.getLogger(__name__)


class CharacterCreationService:
    """
    Application Service for transactional provisioning of new Companion Characters.
    Coordinates Validation, Template Resolution, Personality Compilation, DNA Construction,
    and Atomic Database Persistence.
    """

    def __init__(self, db_session: Any, registry_repo: Optional[CharacterRegistryRepository] = None):
        self.db = db_session
        self.registry_repo = registry_repo or CharacterRegistryRepository(db_session)

    async def preview_character(self, request: CharacterCreationRequest) -> dict:
        """
        Generates a compiled preview of the character without database persistence.
        """
        # Resolve Template & Compile Personality
        template = CharacterTemplateRegistry.get_template(request.template_id)
        personality = PersonalityCompiler.compile(
            template=template,
            mbti=request.mbti,
            keywords=request.personality_keywords
        )
        return CharacterFactory.build_preview(request, template, personality)

    async def create_character(self, request: CharacterCreationRequest) -> CharacterCreationResult:
        """
        Atomically creates a new character with compiled DNA and initial runtime state.
        Guarantees that newly created character is Inactive by default.
        """
        # 1. Fetch existing companion names for duplicate prevention
        existing_companions = await self.registry_repo.list_by_user(request.user_id)
        existing_names = [c.name for c in existing_companions]

        # 2. Validation
        CharacterCreationValidator.validate(request, existing_names)

        # 3. Resolve Template & Compile Personality
        template = CharacterTemplateRegistry.get_template(request.template_id)
        personality = PersonalityCompiler.compile(
            template=template,
            mbti=request.mbti,
            keywords=request.personality_keywords
        )

        # 4. Generate Companion ID & Compile DNA
        name_slug = "".join(c for c in dna_name if c.isalnum()).lower() if 'dna_name' in locals() else ""
        companion_id = f"c_{uuid.uuid4().hex[:12]}"
        dna = CharacterFactory.build_character_dna(
            companion_id=companion_id,
            request=request,
            template=template,
            personality=personality
        )

        # 5. Transactional Persistence
        try:
            # 5.1 Companion Core Record
            companion_entity = Companion(
                id=companion_id,
                user_id=request.user_id,
                name=dna.identity.name,
                is_system_character=False,
                lifecycle_status="available"
            )
            self._add_to_session(companion_entity)

            # 5.2 Character Profile
            profile_entity = CharacterProfileModel(
                id=dna.identity.id,
                companion_id=companion_id,
                name=dna.identity.name,
                display_name=dna.identity.display_name,
                age_appearance=dna.identity.age_appearance,
                gender_expression=dna.identity.gender_expression,
                origin_story=dna.identity.origin_story,
                self_description=dna.identity.self_description,
                core_identity=dna.identity.core_identity,
                version=1
            )
            self._add_to_session(profile_entity)

            # 5.3 Personality Profile
            personality_entity = CharacterPersonalityModel(
                companion_id=companion_id,
                mbti_type=dna.personality.mbti_type,
                openness=dna.personality.openness,
                conscientiousness=dna.personality.conscientiousness,
                extraversion=dna.personality.extraversion,
                agreeableness=dna.personality.agreeableness,
                neuroticism=dna.personality.neuroticism,
                humor_level=dna.personality.humor_level,
                curiosity_level=dna.personality.curiosity_level,
                empathy_level=dna.personality.empathy_level,
                assertiveness=dna.personality.assertiveness,
                playfulness=dna.personality.playfulness,
                emotional_expressiveness=dna.personality.emotional_expressiveness,
                communication_directness=dna.personality.communication_directness,
                warmth=dna.personality.warmth,
                intellectuality=dna.personality.intellectuality
            )
            self._add_to_session(personality_entity)

            # 5.4 Character Values
            values_entity = CharacterValueModel(
                companion_id=companion_id,
                curiosity=dna.values.curiosity,
                honesty=dna.values.honesty,
                loyalty=dna.values.loyalty,
                independence=dna.values.independence,
                kindness=dna.values.kindness,
                growth_orientation=dna.values.growth_orientation,
                humor=dna.values.humor
            )
            self._add_to_session(values_entity)

            # 5.5 Initial Emotion State (Neutral / Calm Baseline)
            emotion_entity = EmotionState(
                companion_id=companion_id,
                primary_emotion=EmotionType.CALM if dna.personality.warmth > 0.6 else EmotionType.NEUTRAL,
                valence=dna.emotion_baseline.get("valence", 0.0),
                arousal=dna.emotion_baseline.get("arousal", 0.0),
                warmth=dna.emotion_baseline.get("warmth", 0.5),
                engagement=dna.emotion_baseline.get("engagement", 0.5),
                tension=0.0
            )
            self._add_to_session(emotion_entity)

            # 5.6 Initial Relationship State
            rel_type = dna.relationship_defaults.get("relationship_type", "acquaintance")
            rel_level = RelationshipLevel.CLOSE if rel_type == "intimate" else RelationshipLevel.ACQUAINTANCE
            relationship_entity = RelationshipState(
                companion_id=companion_id,
                user_id=request.user_id,
                closeness=dna.relationship_defaults.get("initial_closeness", 0.25),
                stage=dna.relationship_defaults.get("initial_stage", "acquaintance"),
                relationship_level=rel_level
            )
            self._add_to_session(relationship_entity)

            # 5.7 Avatar Profile
            avatar_entity = AvatarProfile(
                id=str(uuid.uuid4()),
                companion_id=companion_id,
                visual_style=dna.avatar_preset,
                avatar_type="2d_character",
                default_expression="neutral",
                default_motion="idle"
            )
            self._add_to_session(avatar_entity)

            # 5.8 Presentation Profile (SB-6 / SB-8)
            presentation_entity = CharacterPresentationProfileModel(
                companion_id=companion_id,
                voice_config={
                    "provider": "OPENAI",
                    "voice_id": dna.voice_id,
                    "persona_type": "WARM_COMPANION",
                    "speaking_rate": 1.0,
                    "pitch_offset": 0.0,
                    "warmth": dna.personality.warmth,
                    "energy": dna.personality.extraversion,
                    "empathy": dna.personality.empathy_level
                },
                avatar_config={
                    "avatar_id": dna.avatar_preset,
                    "visual_style": dna.avatar_preset,
                    "default_expression": "neutral",
                    "default_motion": "idle"
                },
                expression_config={
                    "style": dna.speaking_style,
                    "gaze_style": "natural_eye_contact",
                    "available_expressions": ["neutral", "happy", "surprised", "thinking"]
                },
                gesture_config={
                    "style": "natural",
                    "frequency": "natural",
                    "available_gestures": ["idle", "gentle_nod", "soft_wave"]
                }
            )
            self._add_to_session(presentation_entity)

            # 5.9 Initial Character DNA Version 1 (SB-5 Evolution Root)
            initial_snapshot = {
                "identity": {
                    "name": dna.identity.name,
                    "display_name": dna.identity.display_name,
                    "role_title": request.role_title or template.default_role_title,
                    "origin_story": dna.identity.origin_story
                },
                "personality": {
                    "mbti": dna.personality.mbti_type,
                    "openness": dna.personality.openness,
                    "conscientiousness": dna.personality.conscientiousness,
                    "extraversion": dna.personality.extraversion,
                    "agreeableness": dna.personality.agreeableness,
                    "neuroticism": dna.personality.neuroticism,
                    "warmth": dna.personality.warmth,
                    "assertiveness": dna.personality.assertiveness,
                    "intellectuality": dna.personality.intellectuality
                },
                "values": {
                    "curiosity": dna.values.curiosity,
                    "honesty": dna.values.honesty,
                    "loyalty": dna.values.loyalty,
                    "kindness": dna.values.kindness
                },
                "speech_principles": {
                    "speaking_style": dna.speaking_style,
                    "voice_id": dna.voice_id,
                    "speech_profile": dna.speech_profile
                },
                "interests": dna.interests,
                "behavior_rules": dna.behavior_rules,
                "avatar_preset": dna.avatar_preset
            }
            version_entity = CharacterVersionModel(
                companion_id=companion_id,
                version=1,
                dna_snapshot=initial_snapshot,
                change_type="initial"
            )
            self._add_to_session(version_entity)

            # 5.9 Commit Transaction
            await self._commit_session()

            logger.info(f"[CharacterCreationService] Successfully created companion '{dna.identity.name}' ({companion_id}) for user '{request.user_id}'")

            return CharacterCreationResult(
                companion_id=companion_id,
                user_id=request.user_id,
                name=dna.identity.name,
                role_title=request.role_title or template.default_role_title,
                dna=dna,
                is_active=False,
                status="created",
                message=f"Character '{dna.identity.name}' successfully provisioned."
            )

        except Exception as e:
            logger.error(f"[CharacterCreationService] Creation transaction failed, rolling back: {e}")
            await self._rollback_session()
            raise

    def _add_to_session(self, entity: Any):
        if hasattr(self.db, "add"):
            self.db.add(entity)

    async def _commit_session(self):
        if hasattr(self.db, "commit"):
            if asyncio.iscoroutinefunction(self.db.commit):
                await self.db.commit()
            else:
                self.db.commit()

    async def _rollback_session(self):
        if hasattr(self.db, "rollback"):
            if asyncio.iscoroutinefunction(self.db.rollback):
                await self.db.rollback()
            else:
                self.db.rollback()
