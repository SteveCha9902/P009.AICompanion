from typing import Optional, List
from pydantic import BaseModel, Field


class CharacterSummaryResponse(BaseModel):
    """
    API Response Schema for character summary item.
    """
    companion_id: str = Field(..., description="Unique companion runtime identifier")
    name: str = Field(..., description="Character display name")
    role_title: Optional[str] = Field(default="AI Companion", description="Character role or persona title")
    avatar_preview: Optional[str] = Field(default=None, description="Avatar preview asset path or preset")
    voice_name: Optional[str] = Field(default=None, description="Assigned voice persona name")
    is_active: bool = Field(default=False, description="Whether this character is currently active")


class CharacterSummaryListResponse(BaseModel):
    """
    API Response Schema for character list.
    """
    characters: List[CharacterSummaryResponse] = Field(default_factory=list)
    total_count: int = Field(default=0)


class ActivateCharacterResponse(BaseModel):
    """
    API Response Schema for character activation result.
    """
    active_companion_id: str = Field(..., description="Activated companion ID")
    character: CharacterSummaryResponse = Field(..., description="Detailed active character summary")
    message: str = Field(default="Character activated successfully")


class CharacterCreateRequest(BaseModel):
    """
    API Request Schema for creating a new companion character.
    """
    name: str = Field(..., description="Name of the new character", min_length=1, max_length=50)
    template_id: Optional[str] = Field(default="custom", description="Template archetype ID (e.g. lovely_daughter, close_friend)")
    role_title: Optional[str] = Field(default=None, description="Role or persona title (e.g. 사랑스러운 딸)")
    tagline: Optional[str] = Field(default=None, description="One-line summary or tagline")
    relationship_type: Optional[str] = Field(default="family", description="Initial relationship type (e.g. family, friend, romantic, mentor)")
    mbti: Optional[str] = Field(default="INFJ", description="MBTI personality type (e.g. ESFP, ENTJ, INFJ)")
    personality_keywords: List[str] = Field(default_factory=list, description="Personality keywords for trait tuning")
    interests: List[str] = Field(default_factory=list, description="Structured interests (e.g. 노래, 미술, 아이돌)")
    speaking_style: Optional[str] = Field(default=None, description="Speaking tone and style")
    speech_profile: Optional[dict] = Field(default_factory=dict, description="Speech profile configurations (tone, formality, emoji)")
    voice_id: Optional[str] = Field(default=None, description="Assigned voice profile ID (e.g. shimmer, nova, alloy)")
    avatar_preset: Optional[str] = Field(default=None, description="Assigned avatar preset (e.g. lovely_daughter_2d)")
    behavior_rules: List[str] = Field(default_factory=list, description="Custom behavioral guidelines")
    origin_story: Optional[str] = Field(default=None, description="Optional background story")


class CharacterPreviewRequest(BaseModel):
    """
    API Request Schema for compiling a preview of character DNA before persistence.
    """
    name: str = Field(default="미리보기", description="Name of the character")
    template_id: Optional[str] = Field(default="custom", description="Template archetype ID")
    role_title: Optional[str] = Field(default="AI 컴패니언", description="Role or persona title")
    tagline: Optional[str] = Field(default=None, description="One-line summary or tagline")
    relationship_type: Optional[str] = Field(default="family", description="Relationship type")
    mbti: Optional[str] = Field(default="ESFP", description="MBTI personality type")
    personality_keywords: List[str] = Field(default_factory=list, description="Personality keywords")
    interests: List[str] = Field(default_factory=list, description="Structured interests")
    speaking_style: Optional[str] = Field(default=None, description="Speaking tone and style")
    speech_profile: Optional[dict] = Field(default_factory=dict, description="Speech profile configurations")
    voice_id: Optional[str] = Field(default="shimmer", description="Voice profile ID")
    avatar_preset: Optional[str] = Field(default="lovely_daughter_2d", description="Avatar preset")
    behavior_rules: List[str] = Field(default_factory=list, description="Custom behavioral guidelines")
    origin_story: Optional[str] = Field(default=None, description="Optional background story")


class CharacterPreviewResponse(BaseModel):
    """
    API Response Schema for compiled character preview (Non-persisted).
    """
    name: str = Field(..., description="Character name")
    role_title: str = Field(..., description="Role title")
    tagline: Optional[str] = Field(default=None, description="Tagline")
    mbti: str = Field(..., description="Compiled MBTI")
    personality_traits: dict = Field(..., description="Compiled Big-5 and trait vector")
    values: dict = Field(..., description="Compiled character values")
    relationship_seed: dict = Field(..., description="Initial relationship seed")
    interests: List[str] = Field(default_factory=list, description="Structured interests")
    speech_profile: dict = Field(default_factory=dict, description="Speech profile")
    voice: dict = Field(..., description="Voice binding config")
    avatar: dict = Field(..., description="Avatar binding config")
    behavior_rules: List[str] = Field(default_factory=list, description="Behavioral rules")
    origin_story: Optional[str] = Field(default=None, description="Origin story")


class CharacterCreateResponse(BaseModel):
    """
    API Response Schema for character creation result.
    """
    companion_id: str = Field(..., description="Unique generated companion identifier")
    name: str = Field(..., description="Created character name")
    role_title: str = Field(..., description="Role title")
    status: str = Field(default="created", description="Creation status")
    is_active: bool = Field(default=False, description="Created characters are inactive by default")
    message: str = Field(default="Character created successfully")


class CharacterUpdateRequest(BaseModel):
    """
    API Request Schema for updating / evolving an existing character.
    """
    role_title: Optional[str] = Field(default=None, description="Updated role title")
    mbti: Optional[str] = Field(default=None, description="Updated MBTI type")
    personality_keywords: Optional[List[str]] = Field(default=None, description="Updated personality keywords")
    speaking_style: Optional[str] = Field(default=None, description="Updated speaking tone and style")
    voice_id: Optional[str] = Field(default=None, description="Updated voice ID")
    avatar_preset: Optional[str] = Field(default=None, description="Updated avatar preset")
    origin_story: Optional[str] = Field(default=None, description="Updated origin background story")


class CharacterLifecycleResponse(BaseModel):
    """
    API Response Schema for lifecycle status mutations (update, archive, restore, delete).
    """
    companion_id: str = Field(..., description="Companion identifier")
    name: str = Field(..., description="Companion name")
    status: str = Field(..., description="Current lifecycle status or transition")
    character: CharacterSummaryResponse = Field(..., description="Updated character summary")
    message: str = Field(default="Lifecycle transition applied successfully")


class CharacterVersionResponse(BaseModel):
    """
    API Response Schema for Character DNA Version snapshot item.
    """
    version: int = Field(..., description="Version number")
    change_type: str = Field(..., description="Change classification: initial, cosmetic, minor, major")
    dna_snapshot: dict = Field(..., description="JSON snapshot of Character DNA")
    created_at: Optional[str] = Field(default=None, description="Timestamp of version creation")


class CharacterPresentationResponse(BaseModel):
    """
    API Response Schema for Character Presentation Profile (Voice + Avatar + Expression + Gesture).
    """
    companion_id: str = Field(..., description="Companion identifier")
    voice: dict = Field(..., description="Voice rendering configuration")
    avatar: dict = Field(..., description="Avatar visual style and animation baseline")
    expression: dict = Field(..., description="Facial expression and eye contact style")
    gesture: dict = Field(..., description="Body gesture and motion style")


class CharacterPresentationUpdateRequest(BaseModel):
    """
    API Request Schema for updating character-specific presentation profile.
    """
    voice: Optional[dict] = Field(default=None, description="Voice updates (provider, voice_id, speed, pitch, etc.)")
    avatar: Optional[dict] = Field(default=None, description="Avatar updates (avatar_id, visual_style, expression, motion)")
    expression: Optional[dict] = Field(default=None, description="Expression updates (style, gaze_style, available_expressions)")
    gesture: Optional[dict] = Field(default=None, description="Gesture updates (style, frequency, available_gestures)")
