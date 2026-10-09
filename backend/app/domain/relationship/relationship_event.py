import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class RelationshipEventType(str, Enum):
    FIRST_CONVERSATION = "first_conversation"
    PERSONAL_STORY_SHARED = "personal_story_shared"
    USER_SHOWED_TRUST = "user_showed_trust"
    USER_REQUESTED_ADVICE = "user_requested_advice"
    USER_EXPRESSED_GRATITUDE = "user_expressed_gratitude"
    USER_EXPRESSED_AFFECTION = "user_expressed_affection"
    LONG_ABSENCE = "long_absence"
    RETURN_AFTER_ABSENCE = "return_after_absence"
    CONFLICT = "conflict"
    RECONCILIATION = "reconciliation"
    GENERAL_INTERACTION = "general_interaction"

class RelationshipEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    companion_id: str
    event_type: RelationshipEventType
    delta: Dict[str, float] = Field(default_factory=dict)
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
