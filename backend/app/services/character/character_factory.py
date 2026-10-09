import uuid
from typing import Dict, Any, Optional

from app.domain.character.character_identity import CharacterIdentity
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.character.character_values import CharacterValues
from app.domain.character.character_dna import CharacterDNA
from app.domain.character.character_template import CharacterTemplate
from app.domain.character.creation_request import CharacterCreationRequest


class CharacterFactory:
    """
    Domain Factory responsible for compiling complete CharacterDNA from creation inputs.
    Strictly isolated from persistence layer.
    """

    @classmethod
    def build_identity(
        cls,
        companion_id: str,
        request: CharacterCreationRequest,
        template: CharacterTemplate
    ) -> CharacterIdentity:
        role_title = request.role_title or template.default_role_title
        origin_story = request.origin_story or f"사용자의 신뢰할 수 있는 {role_title}로 생성된 인격체."
        
        return CharacterIdentity(
            id=str(uuid.uuid4()),
            companion_id=companion_id,
            name=request.name.strip(),
            display_name=request.name.strip(),
            age_appearance=26,
            gender_expression="female",
            origin_story=origin_story,
            self_description=f"안녕하세요, 저는 {request.name}입니다. {role_title}로서 사용자와 깊이 교감합니다.",
            core_identity=f"{role_title} {request.name}. 독자적 가치관과 성격을 지닌 독립 AI 인격체."
        )

    @classmethod
    def build_values(
        cls,
        request: CharacterCreationRequest,
        template: CharacterTemplate
    ) -> CharacterValues:
        vals = {
            "curiosity": 0.85,
            "honesty": 0.90,
            "loyalty": 0.90,
            "independence": 0.75,
            "kindness": 0.88,
            "growth_orientation": 0.89,
            "humor": 0.65
        }
        for k, v in template.base_values.items():
            if k in vals:
                vals[k] = v

        return CharacterValues(
            curiosity=vals["curiosity"],
            honesty=vals["honesty"],
            loyalty=vals["loyalty"],
            independence=vals["independence"],
            kindness=vals["kindness"],
            growth_orientation=vals["growth_orientation"],
            humor=vals["humor"]
        )

    @classmethod
    def build_emotion_baseline(
        cls,
        template: CharacterTemplate,
        personality: PersonalityProfile
    ) -> Dict[str, float]:
        return {
            "valence": 0.20 if personality.warmth > 0.7 else 0.05,
            "arousal": 0.15 if personality.extraversion > 0.7 else 0.05,
            "warmth": personality.warmth,
            "engagement": 0.60
        }

    @classmethod
    def build_relationship_defaults(
        cls,
        request: CharacterCreationRequest,
        template: CharacterTemplate
    ) -> Dict[str, Any]:
        rel_type = request.relationship_type or template.default_relationship_type
        if rel_type in ["family", "daughter"]:
            return {
                "relationship_type": "family",
                "initial_closeness": 0.80,
                "initial_stage": "close_bond",
                "trust_score": 0.90,
                "intimacy_score": 0.85,
                "attachment_level": "high"
            }
        elif rel_type in ["intimate", "romantic"]:
            return {
                "relationship_type": "romantic",
                "initial_closeness": 0.90,
                "initial_stage": "intimate",
                "trust_score": 0.92,
                "intimacy_score": 0.90,
                "attachment_level": "deep"
            }
        elif rel_type == "mentor":
            return {
                "relationship_type": "mentor",
                "initial_closeness": 0.60,
                "initial_stage": "respected",
                "trust_score": 0.85,
                "intimacy_score": 0.55,
                "attachment_level": "respectful"
            }
        elif rel_type == "friend":
            return {
                "relationship_type": "friend",
                "initial_closeness": 0.65,
                "initial_stage": "friend",
                "trust_score": 0.70,
                "intimacy_score": 0.65,
                "attachment_level": "balanced"
            }
        else:
            return {
                "relationship_type": "acquaintance",
                "initial_closeness": 0.25,
                "initial_stage": "acquaintance",
                "trust_score": 0.50,
                "intimacy_score": 0.50,
                "attachment_level": "neutral"
            }

    @classmethod
    def build_character_dna(
        cls,
        companion_id: str,
        request: CharacterCreationRequest,
        template: CharacterTemplate,
        personality: PersonalityProfile
    ) -> CharacterDNA:
        identity = cls.build_identity(companion_id, request, template)
        values = cls.build_values(request, template)
        emotion_baseline = cls.build_emotion_baseline(template, personality)
        relationship_defaults = cls.build_relationship_defaults(request, template)

        speaking_style = request.speaking_style or template.default_speaking_style
        avatar_preset = request.avatar_preset or template.default_avatar_preset
        voice_id = request.voice_id or template.default_voice_id
        tagline = request.tagline or f"{request.name} - {identity.core_identity}"
        interests = request.interests or ["대화", "일상 공유"]
        speech_profile = request.speech_profile or {"tone": speaking_style, "formality": "natural"}
        behavior_rules = request.behavior_rules or ["상대방의 말을 먼저 이해하려고 한다", "자신의 정체성을 유지한다"]

        return CharacterDNA(
            identity=identity,
            personality=personality,
            values=values,
            speaking_style=speaking_style,
            avatar_preset=avatar_preset,
            voice_id=voice_id,
            tagline=tagline,
            interests=interests,
            speech_profile=speech_profile,
            behavior_rules=behavior_rules,
            emotion_baseline=emotion_baseline,
            relationship_defaults=relationship_defaults
        )

    @classmethod
    def build_preview(
        cls,
        request: CharacterCreationRequest,
        template: CharacterTemplate,
        personality: PersonalityProfile
    ) -> Dict[str, Any]:
        """
        Builds a non-persisted Character Preview response dictionary.
        """
        temp_id = f"preview_{uuid.uuid4().hex[:8]}"
        dna = cls.build_character_dna(temp_id, request, template, personality)

        return {
            "name": dna.identity.name,
            "role_title": request.role_title or template.default_role_title,
            "tagline": dna.tagline,
            "mbti": personality.mbti_type,
            "personality_traits": {
                "openness": personality.openness,
                "conscientiousness": personality.conscientiousness,
                "extraversion": personality.extraversion,
                "agreeableness": personality.agreeableness,
                "neuroticism": personality.neuroticism,
                "warmth": personality.warmth,
                "empathy_level": personality.empathy_level,
                "humor_level": personality.humor_level,
                "playfulness": personality.playfulness,
                "curiosity_level": personality.curiosity_level,
            },
            "values": {
                "kindness": dna.values.kindness,
                "honesty": dna.values.honesty,
                "loyalty": dna.values.loyalty,
                "humor": dna.values.humor,
                "growth_orientation": dna.values.growth_orientation,
            },
            "relationship_seed": dna.relationship_defaults,
            "interests": dna.interests,
            "speech_profile": dna.speech_profile,
            "voice": {
                "voice_id": dna.voice_id,
                "provider": "OPENAI"
            },
            "avatar": {
                "avatar_preset": dna.avatar_preset,
                "visual_style": "2D_Lively"
            },
            "behavior_rules": dna.behavior_rules,
            "origin_story": dna.identity.origin_story
        }
