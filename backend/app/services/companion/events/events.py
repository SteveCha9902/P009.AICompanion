from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class EventPriority(str, Enum):
    SYNC = "sync"       # Critical path, must block or complete immediately
    ASYNC = "async"     # Background task, fire and forget

class EventType(str, Enum):
    USER_INPUT_RECEIVED = "USER_INPUT_RECEIVED"
    CONTEXT_ASSEMBLED = "CONTEXT_ASSEMBLED"
    LLM_CANDIDATE_GENERATED = "LLM_CANDIDATE_GENERATED"
    STATE_VALIDATED = "STATE_VALIDATED"
    PRESENTATION_RESOLVED = "PRESENTATION_RESOLVED"
    
    # Specific async triggers
    INTERACTION_COMPLETED = "INTERACTION_COMPLETED"
    MEMORY_EXTRACTION_REQUESTED = "MEMORY_EXTRACTION_REQUESTED"
    RELATIONSHIP_UPDATE_REQUESTED = "RELATIONSHIP_UPDATE_REQUESTED"
    REFLECTION_REQUESTED = "REFLECTION_REQUESTED"
    REFLECTION_COMPLETED = "REFLECTION_COMPLETED"
    MEMORY_CONSOLIDATED = "MEMORY_CONSOLIDATED"
    
    # Real-time state
    TTS_STARTED = "TTS_STARTED"
    TTS_STOPPED = "TTS_STOPPED"


class CompanionEvent(BaseModel):
    event_id: str
    interaction_id: str
    event_type: EventType
    priority: EventPriority
    timestamp: datetime = datetime.now(timezone.utc)
    payload: Dict[str, Any]
