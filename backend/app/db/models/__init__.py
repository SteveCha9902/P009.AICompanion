from app.db.base import Base
from app.db.models.user import User
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.companion import Companion
from app.db.models.persona import Persona
from app.db.models.memory import Memory
from app.db.models.emotion import EmotionState, EmotionEvent
from app.db.models.relationship import RelationshipState, RelationshipEvent, RelationshipAnchorModel

from app.db.models.presence import PresenceState, PresenceStateEnum
from app.db.models.proactive import ProactiveEvent, ProactiveSettings, ProactiveTriggerType, ProactiveDecision
from app.db.models.notification import NotificationEvent, NotificationSettings, NotificationStatus
from app.db.models.voice_session import VoiceSession, VoiceSessionStatus
from app.db.models.vision import VisionSession, VisionSessionStatus, VisionObservation
from app.db.models.avatar import AvatarProfile
from app.db.models.interaction_session import InteractionSession, InteractionSessionState, PendingInteraction
from app.db.models.character_profile import CharacterProfileModel
from app.db.models.character_personality import CharacterPersonalityModel
from app.db.models.character_value import CharacterValueModel
from app.db.models.character_preference import CharacterPreferenceModel
from app.db.models.character_boundary import CharacterBoundaryModel
from app.db.models.autobiographical_memory import (
    EpisodicMemoryModel,
    LifeEventModel,
    SharedExperienceModel,
    TimelineEventModel,
    StoryChapterModel
)
from app.db.models.reflection import ReflectionRecordModel
from app.db.models.character_decision import CharacterDecisionModel
from app.db.models.character_growth import (
    CharacterGlobalGrowthModel,
    UserRelationshipAdaptationModel,
    RelationshipMilestoneModel
)
from app.db.models.character_agency import AgencyActionModel
from app.db.models.user_character_preference import UserCharacterPreference
from app.db.models.character_version import CharacterVersionModel
from app.db.models.character_presentation_profile import CharacterPresentationProfileModel

# Exporting models and Base for Alembic to autogenerate schema
__all__ = [
    "Base", "User", "Conversation", "Message", "Companion", 
    "Persona", "Memory", "EmotionState", "EmotionEvent", 
    "RelationshipState", "RelationshipEvent", "RelationshipAnchorModel",
    "PresenceState", "ProactiveEvent", "ProactiveSettings",
    "NotificationEvent", "NotificationSettings", "VoiceSession", "VoiceSessionStatus",
    "VisionSession", "VisionSessionStatus", "VisionObservation", "AvatarProfile",
    "InteractionSession", "InteractionSessionState", "PendingInteraction",
    "CharacterProfileModel", "CharacterPersonalityModel", "CharacterValueModel",
    "CharacterPreferenceModel", "CharacterBoundaryModel",
    "EpisodicMemoryModel", "LifeEventModel", "SharedExperienceModel",
    "TimelineEventModel", "StoryChapterModel", "ReflectionRecordModel",
    "CharacterDecisionModel", "CharacterGlobalGrowthModel",
    "UserRelationshipAdaptationModel", "RelationshipMilestoneModel",
    "AgencyActionModel", "UserCharacterPreference", "CharacterVersionModel",
    "CharacterPresentationProfileModel"
]




