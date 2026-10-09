from typing import List, Optional
from pydantic import BaseModel, Field

class ResponseStyle(BaseModel):
    warmth: float = Field(default=0.84, ge=0.0, le=1.0)
    humor: float = Field(default=0.62, ge=0.0, le=1.0)
    directness: float = Field(default=0.48, ge=0.0, le=1.0)
    playfulness: float = Field(default=0.73, ge=0.0, le=1.0)

class InteractionBehavior(BaseModel):
    ask_followup: bool = Field(default=True)
    tease_user: bool = Field(default=False)
    show_concern: bool = Field(default=True)
    initiate_topic: bool = Field(default=True)

class EmotionalExpressionDirective(BaseModel):
    expression: str = Field(default="gentle_smile")
    intensity: float = Field(default=0.67, ge=0.0, le=1.0)

class BehaviorDirective(BaseModel):
    """
    Actionable directive output by PersonalityBehaviorEngine (<10ms).
    Injected into ContextBuilder to steer LLM expression.
    """
    response_style: ResponseStyle = Field(default_factory=ResponseStyle)
    interaction_behavior: InteractionBehavior = Field(default_factory=InteractionBehavior)
    emotional_expression: EmotionalExpressionDirective = Field(default_factory=EmotionalExpressionDirective)
    reasons: List[str] = Field(default_factory=list, description="Explainable decision rationale")
