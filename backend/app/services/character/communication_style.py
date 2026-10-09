from typing import Optional
from pydantic import BaseModel, Field

class CommunicationStyle(BaseModel):
    """
    Detailed communication styling parameters shaping tone, structure, and expression.
    """
    sentence_length: str = Field(default="natural", description="short | medium | long | natural")
    formality: float = Field(default=0.2, ge=0.0, le=1.0, description="0.0 = casual/intimate, 1.0 = formal")
    humor: float = Field(default=0.6, ge=0.0, le=1.0, description="Frequency and playfulness of humor")
    emoji_usage: float = Field(default=0.4, ge=0.0, le=1.0, description="Density of emojis")
    emotional_expression: float = Field(default=0.8, ge=0.0, le=1.0, description="Expressiveness of empathy and feelings")
    question_frequency: float = Field(default=0.5, ge=0.0, le=1.0, description="Active conversational curiosity")
