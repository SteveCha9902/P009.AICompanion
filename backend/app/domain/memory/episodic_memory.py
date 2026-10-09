import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class EpisodicMemory(BaseModel):
    """
    Episodic Memory representing a specific interaction episode or conversational moment.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    companion_id: str = "default_companion"
    conversation_id: Optional[str] = None
    interaction_id: Optional[str] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    summary: str
    participants: List[str] = Field(default_factory=lambda: ["user", "companion"])
    emotional_context: Dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    event_type: str = "CONVERSATION_EPISODE"
    embedding_id: Optional[str] = None
