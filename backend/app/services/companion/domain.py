import json
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class InputType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    VISION = "vision"
    SYSTEM = "system"

import uuid

class NormalizedInput(BaseModel):
    interaction_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    companion_id: Optional[str] = None
    conversation_id: str = "default"
    input_type: InputType = Field(default=InputType.TEXT, alias="modality")
    content: str  # text or transcript
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

# LLM Output Candidates
class EmotionCandidate(BaseModel):
    primary: str
    intensity: float = 0.5

class RelationshipSignal(BaseModel):
    type: str
    confidence: float = 0.5

class PresentationHint(BaseModel):
    expression: str = "neutral"
    energy: float = 0.5
    animation: str = "idle"
    gaze: str = "user"
    
class StructuredCandidate(BaseModel):
    response_text: str
    emotion_candidate: Optional[EmotionCandidate] = None
    relationship_signal: Optional[RelationshipSignal] = None
    memory_candidates: List[str] = Field(default_factory=list)
    presentation: Optional[PresentationHint] = None

class UnifiedResponse(BaseModel):
    interaction_id: str
    text: str
    avatar_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# SSE Event Types
class SSEEventType(str, Enum):
    INTERACTION_STARTED = "interaction_started"
    THINKING = "thinking"
    TEXT_DELTA = "text_delta"
    TEXT_COMPLETED = "text_completed"
    AVATAR_STATE = "avatar_state"
    INTERACTION_COMPLETED = "interaction_completed"
    ERROR = "error"

def format_sse_event(event_type: SSEEventType, data: Any, event_id: Optional[str] = None) -> str:
    """Formats payload into a standard JSON SSE message with optional id."""
    if isinstance(data, (dict, list, str, int, float, bool)):
        data_str = json.dumps(data) if not isinstance(data, str) else json.dumps({"message": data})
    elif hasattr(data, "model_dump"):
        data_str = json.dumps(data.model_dump())
    elif hasattr(data, "dict"):
        data_str = json.dumps(data.dict())
    else:
        data_str = json.dumps({"raw": str(data)})
    
    id_header = f"id: {event_id}\n" if event_id else ""
    return f"{id_header}event: {event_type.value}\ndata: {data_str}\n\n"
