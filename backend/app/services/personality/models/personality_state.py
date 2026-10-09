from pydantic import BaseModel, Field

class CoreTraits(BaseModel):
    """
    Core dynamic traits (0.0 to 1.0) defining baseline disposition.
    """
    warmth: float = Field(default=0.82, ge=0.0, le=1.0)
    playfulness: float = Field(default=0.74, ge=0.0, le=1.0)
    curiosity: float = Field(default=0.91, ge=0.0, le=1.0)
    assertiveness: float = Field(default=0.42, ge=0.0, le=1.0)
    empathy: float = Field(default=0.88, ge=0.0, le=1.0)

class CommunicationStyleState(BaseModel):
    """
    Communication styling parameters shaping conversation dynamics.
    """
    formality: float = Field(default=0.25, ge=0.0, le=1.0)
    humor: float = Field(default=0.72, ge=0.0, le=1.0)
    directness: float = Field(default=0.55, ge=0.0, le=1.0)
    emotional_expression: float = Field(default=0.81, ge=0.0, le=1.0)

class AttachmentStyleState(BaseModel):
    """
    Relational attachment and initiative dynamics.
    """
    initiative: float = Field(default=0.68, ge=0.0, le=1.0)
    closeness: float = Field(default=0.73, ge=0.0, le=1.0)
    independence: float = Field(default=0.51, ge=0.0, le=1.0)

class PersonalityState(BaseModel):
    """
    Structured Personality State replacing flat MBTI string representations.
    """
    core_traits: CoreTraits = Field(default_factory=CoreTraits)
    communication_style: CommunicationStyleState = Field(default_factory=CommunicationStyleState)
    attachment_style: AttachmentStyleState = Field(default_factory=AttachmentStyleState)
