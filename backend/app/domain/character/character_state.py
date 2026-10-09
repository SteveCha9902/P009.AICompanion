from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ResponseStrategy(BaseModel):
    """
    Independent Character Agency output determining how the character responds to user input.
    """
    agree: bool = True
    challenge_user: bool = False
    ask_question: bool = True
    provide_support: bool = True
    playful_response: bool = False
    assert_boundary: bool = False
    reasoning: Optional[str] = None

class CharacterState(BaseModel):
    """
    Dynamic snapshot combining static personality traits with real-time emotional & relational states.
    """
    companion_id: str = "default_companion"
    active_mbti: str = "ENFP"
    effective_warmth: float = 0.8
    effective_intellectuality: float = 0.7
    effective_humor: float = 0.6
    effective_directness: float = 0.5
    current_mood: str = "warm"
    relationship_level: str = "friend"
    energy: float = Field(default=0.7, ge=0.0, le=1.0)
    active_strategy: ResponseStrategy = Field(default_factory=ResponseStrategy)

