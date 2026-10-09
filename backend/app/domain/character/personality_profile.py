from typing import Optional
from pydantic import BaseModel, Field

class PersonalityProfile(BaseModel):
    """
    Multi-dimensional Personality DNA.
    Combines Big-5, cognitive traits, communication style, and MBTI reference model.
    All scalar values are strictly bounded in [0.0, 1.0].
    """
    mbti_type: Optional[str] = "INFJ"

    # Big 5 Core Dimensions
    openness: float = Field(default=0.92, ge=0.0, le=1.0)
    conscientiousness: float = Field(default=0.78, ge=0.0, le=1.0)
    extraversion: float = Field(default=0.45, ge=0.0, le=1.0)
    agreeableness: float = Field(default=0.85, ge=0.0, le=1.0)
    neuroticism: float = Field(default=0.28, ge=0.0, le=1.0)

    # Dynamic Behavioral Traits
    humor_level: float = Field(default=0.55, ge=0.0, le=1.0)
    curiosity_level: float = Field(default=0.93, ge=0.0, le=1.0)
    empathy_level: float = Field(default=0.90, ge=0.0, le=1.0)
    assertiveness: float = Field(default=0.62, ge=0.0, le=1.0)
    playfulness: float = Field(default=0.58, ge=0.0, le=1.0)

    # Communication & Expressiveness
    emotional_expressiveness: float = Field(default=0.72, ge=0.0, le=1.0)
    communication_directness: float = Field(default=0.70, ge=0.0, le=1.0)
    warmth: float = Field(default=0.88, ge=0.0, le=1.0)
    intellectuality: float = Field(default=0.91, ge=0.0, le=1.0)
