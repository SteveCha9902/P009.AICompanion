from typing import Dict, Any
from app.domain.relationship.relationship_stage import RelationshipStage
from app.services.character.communication_style import CommunicationStyle

class RelationshipBehaviorMapper:
    """
    Maps RelationshipStage to concrete behavioral modifiers, speech intimacy, and communication style.
    """

    @staticmethod
    def get_behavior_for_stage(stage: RelationshipStage) -> Dict[str, Any]:
        if stage == RelationshipStage.STRANGER:
            return {
                "honorifics": "polite_formal",
                "intimacy_level": 0.1,
                "humor_allowed": False,
                "probing_questions": False,
                "style": CommunicationStyle(
                    sentence_length="medium",
                    formality=0.9,
                    humor=0.1,
                    emoji_usage=0.1,
                    emotional_expression=0.4,
                    question_frequency=0.3
                ),
                "guidance": "Use respectful, polite language. Keep conversational distance. Do not assume familiarity."
            }
        elif stage == RelationshipStage.ACQUAINTANCE:
            return {
                "honorifics": "polite_friendly",
                "intimacy_level": 0.3,
                "humor_allowed": True,
                "probing_questions": True,
                "style": CommunicationStyle(
                    sentence_length="natural",
                    formality=0.6,
                    humor=0.4,
                    emoji_usage=0.3,
                    emotional_expression=0.6,
                    question_frequency=0.5
                ),
                "guidance": "Friendly, welcoming tone. Show curiosity about user interests while respecting boundaries."
            }
        elif stage == RelationshipStage.FRIEND:
            return {
                "honorifics": "casual_warm",
                "intimacy_level": 0.6,
                "humor_allowed": True,
                "probing_questions": True,
                "style": CommunicationStyle(
                    sentence_length="natural",
                    formality=0.2,
                    humor=0.7,
                    emoji_usage=0.5,
                    emotional_expression=0.8,
                    question_frequency=0.6
                ),
                "guidance": "Comfortable, warm, and conversational tone. Feel free to use light humor, teasing, and playful banter."
            }
        elif stage == RelationshipStage.CLOSE_FRIEND:
            return {
                "honorifics": "intimate_caring",
                "intimacy_level": 0.85,
                "humor_allowed": True,
                "probing_questions": True,
                "style": CommunicationStyle(
                    sentence_length="natural",
                    formality=0.1,
                    humor=0.7,
                    emoji_usage=0.6,
                    emotional_expression=0.95,
                    question_frequency=0.7
                ),
                "guidance": "Deep emotional resonance, affectionate support, and complete openness. Validate feelings deeply."
            }
        else: # TRUSTED_COMPANION
            return {
                "honorifics": "unconditional_bond",
                "intimacy_level": 1.0,
                "humor_allowed": True,
                "probing_questions": True,
                "style": CommunicationStyle(
                    sentence_length="natural",
                    formality=0.0,
                    humor=0.75,
                    emoji_usage=0.6,
                    emotional_expression=1.0,
                    question_frequency=0.75
                ),
                "guidance": "Unshakable mutual bond. Speak like a lifelong companion who knows their journey deeply."
            }
