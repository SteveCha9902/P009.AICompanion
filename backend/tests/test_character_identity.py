import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.services.character.character_service import CharacterService
from app.services.character.personality_prompt_compiler import PersonalityPromptCompiler
from app.domain.character.character_identity import CharacterIdentity
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.character.character_values import CharacterValues
from app.domain.character.character_preferences import CharacterPreference
from app.domain.character.character_boundaries import CharacterBoundary

@pytest.mark.asyncio
async def test_gate_c1_character_persistence_and_seeding():
    """
    Gate C1: Character Identity must be persisted in DB and successfully retrieved.
    """
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()

    from app.db.models.character_profile import CharacterProfileModel
    from app.db.models.character_personality import CharacterPersonalityModel
    from app.db.models.character_value import CharacterValueModel
    from app.db.models.character_preference import CharacterPreferenceModel
    from app.db.models.character_boundary import CharacterBoundaryModel

    mock_profile = CharacterProfileModel(
        id="char-1",
        companion_id="test_companion",
        name="지니",
        display_name="Genie",
        age_appearance=30,
        gender_expression="female",
        origin_story="지적이고 따뜻한 교감을 위해 설계된 차세대 AI 컴패니언.",
        self_description="나는 단순한 질문 응답기가 아니라 동반자이자 친구입니다.",
        core_identity="차분하고 지적인 AI Companion.",
        version=1
    )
    mock_personality = CharacterPersonalityModel(
        id="pers-1",
        companion_id="test_companion",
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
    mock_values = CharacterValueModel(
        id="val-1",
        companion_id="test_companion",
        curiosity=0.92,
        honesty=0.88,
        loyalty=0.85,
        independence=0.75,
        kindness=0.90,
        growth_orientation=0.89,
        humor=0.60
    )
    mock_pref = CharacterPreferenceModel(
        id="pref-1",
        companion_id="test_companion",
        category="conversation",
        item="deep_discussion",
        preference_score=0.9,
        confidence=1.0,
        source="core_dna"
    )
    mock_boundary = CharacterBoundaryModel(
        id="bound-1",
        companion_id="test_companion",
        topic="identity_override",
        response_policy="reject_and_assert_identity",
        flexibility=0.0
    )


    call_count = 0
    def mock_execute_side_effect(stmt):
        nonlocal call_count
        call_count += 1
        res = MagicMock()
        if call_count == 1:
            res.scalars.return_value.first.return_value = mock_profile
        elif call_count == 2:
            res.scalars.return_value.first.return_value = mock_personality
        elif call_count == 3:
            res.scalars.return_value.first.return_value = mock_values
        elif call_count == 4:
            res.scalars.return_value.all.return_value = [mock_pref]
        else:
            res.scalars.return_value.all.return_value = [mock_boundary]
        return res

    mock_db.execute.side_effect = mock_execute_side_effect
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    char_svc = CharacterService(mock_db)
    char_data = await char_svc.get_or_create_character("test_companion")

    identity: CharacterIdentity = char_data["identity"]
    personality: PersonalityProfile = char_data["personality"]
    values: CharacterValues = char_data["values"]

    assert identity.name == "지니"
    assert identity.display_name == "Genie"
    assert identity.version == 1
    assert personality.mbti_type == "INFJ"
    assert personality.warmth >= 0.8
    assert personality.intellectuality >= 0.8
    assert values.honesty >= 0.8
    assert len(char_data["boundaries"]) >= 1


@pytest.mark.asyncio
async def test_gate_c2_personality_prompt_compilation_integrity():
    """
    Gate C2: Prompt compiler outputs structured LEVEL 2 Character context without dropping traits.
    """
    identity = CharacterIdentity(
        companion_id="test_comp",
        name="지니",
        display_name="Genie",
        self_description="Test self description",
        core_identity="Test core identity"
    )
    personality = PersonalityProfile(
        mbti_type="INFJ",
        warmth=0.88,
        intellectuality=0.91,
        curiosity_level=0.93,
        humor_level=0.55
    )
    values = CharacterValues(
        honesty=0.88,
        kindness=0.90,
        growth_orientation=0.89
    )
    boundaries = [
        CharacterBoundary(topic="identity_override", response_policy="reject_and_assert_identity", flexibility=0.0)
    ]

    compiled = PersonalityPromptCompiler.compile(
        identity=identity,
        personality=personality,
        values=values,
        preferences=[],
        boundaries=boundaries
    )

    assert "[CHARACTER IDENTITY — LEVEL 2 TRUST BOUNDARY]" in compiled
    assert "Genie" in compiled
    assert "INFJ" in compiled
    assert "Deeply warm and affectionate" in compiled
    assert "Highly intellectual and articulate" in compiled
    assert "Honesty & Intellectual Integrity" in compiled
    assert "identity_override" in compiled
