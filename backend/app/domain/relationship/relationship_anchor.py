import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class RelationshipAnchorType(str, Enum):
    FIRST_MEETING = "FIRST_MEETING"
    FIRST_PERSONAL_CONFESSION = "FIRST_PERSONAL_CONFESSION"
    IMPORTANT_SHARED_EVENT = "IMPORTANT_SHARED_EVENT"
    STAGE_UPGRADE = "STAGE_UPGRADE"
    CONFLICT = "CONFLICT"
    RECONCILIATION = "RECONCILIATION"
    MAJOR_LIFE_EVENT = "MAJOR_LIFE_EVENT"

class RelationshipAnchor(BaseModel):
    """
    Immutable Social Anchor representing milestone relational events.
    Persisted permanently even if regular conversation history is cleared.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    companion_id: str
    anchor_type: RelationshipAnchorType
    summary: str
    importance: float = Field(default=0.8, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
