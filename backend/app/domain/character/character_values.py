from pydantic import BaseModel, Field

class CharacterValues(BaseModel):
    """
    Core Value System for the Character.
    Guides ethical judgement, conversational trade-offs, and agency decisions.
    """
    curiosity: float = Field(default=0.92, ge=0.0, le=1.0)
    honesty: float = Field(default=0.88, ge=0.0, le=1.0)
    loyalty: float = Field(default=0.85, ge=0.0, le=1.0)
    independence: float = Field(default=0.75, ge=0.0, le=1.0)
    kindness: float = Field(default=0.90, ge=0.0, le=1.0)
    growth_orientation: float = Field(default=0.89, ge=0.0, le=1.0)
    humor: float = Field(default=0.60, ge=0.0, le=1.0)
