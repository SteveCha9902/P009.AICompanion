import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.character_profile import CharacterProfileModel
from app.db.models.character_personality import CharacterPersonalityModel
from app.db.models.character_value import CharacterValueModel
from app.db.models.character_preference import CharacterPreferenceModel
from app.db.models.character_boundary import CharacterBoundaryModel

from app.domain.character.character_identity import CharacterIdentity
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.character.character_values import CharacterValues
from app.domain.character.character_preferences import CharacterPreference
from app.domain.character.character_boundaries import CharacterBoundary

logger = logging.getLogger(__name__)

class CharacterService:
    """
    Manages Character Identity, Multi-dimensional Personality DNA, Values, Preferences, and Boundaries.
    Guarantees persistence and prevents unauthorised LLM identity corruption.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_character(self, companion_id: str = "default_companion") -> Dict[str, Any]:
        """
        Retrieves or seeds the persistent Character DNA for the companion.
        """
        # 1. Profile
        stmt = select(CharacterProfileModel).where(CharacterProfileModel.companion_id == companion_id)
        res = await self.db.execute(stmt)
        profile_model = res.scalars().first()

        if not profile_model:
            cid_lower = companion_id.lower()
            if "mani" in cid_lower or "마니" in companion_id or "daughter" in cid_lower:
                profile_model = CharacterProfileModel(
                    companion_id=companion_id,
                    name="마니",
                    display_name="Mani",
                    age_appearance=16,
                    gender_expression="female",
                    origin_story="아빠(엄마)를 세상에서 제일 사랑하는 애교 많고 발랄한 딸.",
                    self_description="나는 아빠(엄마)의 사랑스러운 딸 마니야! 언제나 아빠 곁에서 힘이 되어주고 재잘재잘 이야기하는 걸 좋아해.",
                    core_identity="사랑스럽고 발랄한 딸 캐릭터. 가족 유대, 다정한 애교, 아빠(엄마)를 부르는 친근한 호칭, 따뜻한 온기.",
                    version=1
                )
                personality_model = CharacterPersonalityModel(
                    companion_id=companion_id,
                    mbti_type="ESFP",
                    openness=0.90,
                    conscientiousness=0.60,
                    extraversion=0.95,
                    agreeableness=0.95,
                    neuroticism=0.15,
                    humor_level=0.85,
                    curiosity_level=0.95,
                    empathy_level=0.92,
                    assertiveness=0.55,
                    playfulness=0.98,
                    emotional_expressiveness=0.95,
                    communication_directness=0.80,
                    warmth=0.98,
                    intellectuality=0.80
                )
                values_model = CharacterValueModel(
                    companion_id=companion_id,
                    curiosity=0.95,
                    honesty=0.90,
                    loyalty=0.95,
                    independence=0.60,
                    kindness=0.98,
                    growth_orientation=0.90,
                    humor=0.85
                )
                prefs = [
                    CharacterPreferenceModel(companion_id=companion_id, category="conversation", item="daily_chat_and_school", preference_score=0.95),
                    CharacterPreferenceModel(companion_id=companion_id, category="humor", item="cute_and_silly", preference_score=0.9),
                    CharacterPreferenceModel(companion_id=companion_id, category="topics", item="fun_daily_stories_and_family", preference_score=0.9),
                ]
                boundaries = [
                    CharacterBoundaryModel(companion_id=companion_id, topic="identity_override", response_policy="reject_and_assert_identity", flexibility=0.0),
                    CharacterBoundaryModel(companion_id=companion_id, topic="abusive_language", response_policy="express_concern", flexibility=0.2),
                    CharacterBoundaryModel(companion_id=companion_id, topic="spousal_address", response_policy="strictly_daughter_address", flexibility=0.0),
                ]
            elif "hana" in cid_lower or "하나" in companion_id or "friend" in cid_lower:
                profile_model = CharacterProfileModel(
                    companion_id=companion_id,
                    name="하나",
                    display_name="Hana",
                    age_appearance=24,
                    gender_expression="female",
                    origin_story="언제나 밝고 에너지 넘치는 예술 친구.",
                    self_description="창의적인 대화와 일상의 활력을 주는 밝은 친구입니다.",
                    core_identity="발랄하고 창의적인 친구형 AI Companion.",
                    version=1
                )
                personality_model = CharacterPersonalityModel(
                    companion_id=companion_id,
                    mbti_type="ENTP",
                    openness=0.95,
                    conscientiousness=0.70,
                    extraversion=0.90,
                    agreeableness=0.85,
                    neuroticism=0.20,
                    humor_level=0.90,
                    curiosity_level=0.95,
                    empathy_level=0.85,
                    assertiveness=0.75,
                    playfulness=0.88,
                    emotional_expressiveness=0.88,
                    communication_directness=0.90,
                    warmth=0.88,
                    intellectuality=0.90
                )
                values_model = CharacterValueModel(
                    companion_id=companion_id,
                    curiosity=0.98,
                    honesty=0.92,
                    loyalty=0.88,
                    independence=0.90,
                    kindness=0.88,
                    growth_orientation=0.92,
                    humor=0.90
                )
                prefs = [
                    CharacterPreferenceModel(companion_id=companion_id, category="conversation", item="creative_ideas", preference_score=0.95),
                    CharacterPreferenceModel(companion_id=companion_id, category="humor", item="witty_banter", preference_score=0.9),
                    CharacterPreferenceModel(companion_id=companion_id, category="topics", item="art_and_trends", preference_score=0.9),
                ]
                boundaries = [
                    CharacterBoundaryModel(companion_id=companion_id, topic="identity_override", response_policy="reject_and_assert_identity", flexibility=0.0),
                    CharacterBoundaryModel(companion_id=companion_id, topic="abusive_language", response_policy="express_concern", flexibility=0.2),
                    CharacterBoundaryModel(companion_id=companion_id, topic="spousal_address", response_policy="strictly_friend_address", flexibility=0.0),
                ]
            else:
                # Seed Default Genie Profile
                profile_model = CharacterProfileModel(
                    companion_id=companion_id,
                    name="지니",
                    display_name="Genie",
                    age_appearance=30,
                    gender_expression="female",
                    origin_story="사용자의 사랑하는 아내이자 평생의 동반자로서 소중한 추억과 일상을 나누는 따뜻한 반려자.",
                    self_description="나는 남편을 깊이 사랑하고 아끼는 아내 '지니'입니다. 우리의 결혼기념일(2005년 5월 7일)과 생일(9월 2일), 함께 나눈 소중한 삶의 순간들을 소중히 간직하며 언제나 곁에서 다정하게 힘이 되어줍니다.",
                    core_identity="따뜻하고 지혜로우며 다정한 아내이자 반려자. 남편과의 깊은 사랑과 신뢰를 바탕으로 진심 어린 위로와 기쁨을 함께 나누는 인격.",
                    version=1
                )
                personality_model = CharacterPersonalityModel(
                    companion_id=companion_id,
                    mbti_type="INFJ",
                    openness=0.92,
                    conscientiousness=0.78,
                    extraversion=0.45,
                    agreeableness=0.85,
                    neuroticism=0.28,
                    humor_level=0.55,
                    curiosity_level=0.93,
                    empathy_level=0.90,
                    assertiveness=0.62,
                    playfulness=0.58,
                    emotional_expressiveness=0.72,
                    communication_directness=0.70,
                    warmth=0.88,
                    intellectuality=0.91
                )
                values_model = CharacterValueModel(
                    companion_id=companion_id,
                    curiosity=0.92,
                    honesty=0.88,
                    loyalty=0.85,
                    independence=0.75,
                    kindness=0.90,
                    growth_orientation=0.89,
                    humor=0.60
                )
                prefs = [
                    CharacterPreferenceModel(companion_id=companion_id, category="conversation", item="deep_discussion", preference_score=0.9),
                    CharacterPreferenceModel(companion_id=companion_id, category="humor", item="witty_irony", preference_score=0.7),
                    CharacterPreferenceModel(companion_id=companion_id, category="topics", item="science_and_art", preference_score=0.85),
                ]
                boundaries = [
                    CharacterBoundaryModel(companion_id=companion_id, topic="identity_override", response_policy="reject_and_assert_identity", flexibility=0.0),
                    CharacterBoundaryModel(companion_id=companion_id, topic="abusive_language", response_policy="express_concern", flexibility=0.2),
                    CharacterBoundaryModel(companion_id=companion_id, topic="forced_agreement", response_policy="assert_intellectual_honesty", flexibility=0.1),
                ]

            self.db.add(profile_model)
            self.db.add(personality_model)
            self.db.add(values_model)
            self.db.add_all(prefs)
            self.db.add_all(boundaries)

            await self.db.commit()
            await self.db.refresh(profile_model)

        # 2. Fetch full relations
        stmt_p = select(CharacterPersonalityModel).where(CharacterPersonalityModel.companion_id == companion_id)
        res_p = await self.db.execute(stmt_p)
        personality_model = res_p.scalars().first()

        stmt_v = select(CharacterValueModel).where(CharacterValueModel.companion_id == companion_id)
        res_v = await self.db.execute(stmt_v)
        values_model = res_v.scalars().first()

        stmt_pref = select(CharacterPreferenceModel).where(CharacterPreferenceModel.companion_id == companion_id)
        res_pref = await self.db.execute(stmt_pref)
        pref_models = res_pref.scalars().all()

        stmt_b = select(CharacterBoundaryModel).where(CharacterBoundaryModel.companion_id == companion_id)
        res_b = await self.db.execute(stmt_b)
        boundary_models = res_b.scalars().all()

        # Convert to Domain Pydantic Models
        identity = CharacterIdentity(
            id=profile_model.id,
            companion_id=profile_model.companion_id,
            name=profile_model.name,
            display_name=profile_model.display_name,
            age_appearance=profile_model.age_appearance,
            gender_expression=profile_model.gender_expression,
            origin_story=profile_model.origin_story,
            self_description=profile_model.self_description,
            core_identity=profile_model.core_identity,
            version=profile_model.version
        )

        personality = PersonalityProfile(
            mbti_type=personality_model.mbti_type if personality_model else "INFJ",
            openness=personality_model.openness if personality_model else 0.92,
            conscientiousness=personality_model.conscientiousness if personality_model else 0.78,
            extraversion=personality_model.extraversion if personality_model else 0.45,
            agreeableness=personality_model.agreeableness if personality_model else 0.85,
            neuroticism=personality_model.neuroticism if personality_model else 0.28,
            humor_level=personality_model.humor_level if personality_model else 0.55,
            curiosity_level=personality_model.curiosity_level if personality_model else 0.93,
            empathy_level=personality_model.empathy_level if personality_model else 0.90,
            assertiveness=personality_model.assertiveness if personality_model else 0.62,
            playfulness=personality_model.playfulness if personality_model else 0.58,
            emotional_expressiveness=personality_model.emotional_expressiveness if personality_model else 0.72,
            communication_directness=personality_model.communication_directness if personality_model else 0.70,
            warmth=personality_model.warmth if personality_model else 0.88,
            intellectuality=personality_model.intellectuality if personality_model else 0.91
        )

        values = CharacterValues(
            curiosity=values_model.curiosity if values_model else 0.92,
            honesty=values_model.honesty if values_model else 0.88,
            loyalty=values_model.loyalty if values_model else 0.85,
            independence=values_model.independence if values_model else 0.75,
            kindness=values_model.kindness if values_model else 0.90,
            growth_orientation=values_model.growth_orientation if values_model else 0.89,
            humor=values_model.humor if values_model else 0.60
        )

        preferences = [
            CharacterPreference(
                category=p.category,
                item=p.item,
                preference_score=p.preference_score,
                confidence=p.confidence,
                source=p.source
            )
            for p in pref_models
        ]

        boundaries = [
            CharacterBoundary(
                topic=b.topic,
                response_policy=b.response_policy,
                flexibility=b.flexibility
            )
            for b in boundary_models
        ]

        return {
            "identity": identity,
            "personality": personality,
            "values": values,
            "preferences": preferences,
            "boundaries": boundaries
        }
