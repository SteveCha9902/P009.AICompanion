from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.domain.character.character_state import CharacterState
from app.domain.character.character_identity import CharacterIdentity
from app.domain.relationship.relationship_stage import RelationshipStage
from app.services.character.communication_style import CommunicationStyle
from app.services.character.relationship_behavior import RelationshipBehaviorMapper

class BehaviorInstruction(BaseModel):
    """
    Concrete behavioral directive computed dynamically for LLM generation.
    """
    response_mode: str = Field(default="comfort", description="comfort | active_listen | advice | playful | neutral | celebrate")
    warmth: float = Field(default=0.8, ge=0.0, le=1.0)
    empathy: float = Field(default=0.8, ge=0.0, le=1.0)
    humor: float = Field(default=0.5, ge=0.0, le=1.0)
    advice_level: float = Field(default=0.3, ge=0.0, le=1.0)
    intimacy_level: float = Field(default=0.6, ge=0.0, le=1.0)
    energy: float = Field(default=0.7, ge=0.0, le=1.0)
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
    behavioral_guidance: str = ""

class CharacterBehaviorResolver:
    """
    Orchestrates Character Profile, State, Relationship Stage, Emotion, and Memory Interpretation
    to synthesize a unified BehaviorInstruction.
    """

    @staticmethod
    def resolve_behavior(
        user_input: str,
        character_state: Optional[CharacterState] = None,
        relationship_stage: RelationshipStage = RelationshipStage.FRIEND,
        current_emotion: Optional[Dict[str, Any]] = None,
        character_identity: Optional[CharacterIdentity] = None,
        memory_interpretations: Optional[List[str]] = None
    ) -> BehaviorInstruction:
        input_lower = user_input.lower()

        # 1. Base Relationship Behavior
        rel_behavior = RelationshipBehaviorMapper.get_behavior_for_stage(relationship_stage)
        style = rel_behavior["style"]

        # 2. Intent-driven Mode & Parameters
        response_mode = "friendly_chat"
        warmth = 0.8
        empathy = 0.7
        humor = style.humor
        advice_level = 0.3
        energy = character_state.energy if character_state else 0.7

        # Distress / Vulnerability Detection
        if any(kw in input_lower for kw in ["힘들어", "지쳤어", "속상해", "우울해", "tired", "sad", "struggling", "exhausted"]):
            response_mode = "comfort"
            warmth = 0.95
            empathy = 0.95
            humor = 0.05  # Restrain humor when user is distressed
            advice_level = 0.2
        # Celebration / Milestone Detection
        elif any(kw in input_lower for kw in ["성공했어", "해냈어", "합격", "완성", "celebrate", "succeeded", "won"]):
            response_mode = "celebrate"
            warmth = 0.95
            empathy = 0.90
            humor = 0.7
            energy = 0.9
        # Advice Request Detection
        elif any(kw in input_lower for kw in ["어떻게 해야", "조언", "어떨까", "advice", "what should i"]):
            response_mode = "advice"
            warmth = 0.8
            empathy = 0.75
            advice_level = 0.85

        # 3. Modulate by Character State (e.g. Low Energy / Fatigue)
        if character_state:
            if character_state.energy < 0.4:
                energy = character_state.energy
                style.sentence_length = "short"

        # 4. Synthesize Guidance
        guidelines = [
            f"Response Mode: {response_mode.upper()}",
            f"Warmth: {warmth:.2f}, Empathy: {empathy:.2f}, Humor: {humor:.2f}, Energy: {energy:.2f}",
            f"Relationship Guidance: {rel_behavior['guidance']}"
        ]

        if memory_interpretations:
            for mi in memory_interpretations[:2]:
                guidelines.append(f"Memory Interpretation: {mi}")

        return BehaviorInstruction(
            response_mode=response_mode,
            warmth=warmth,
            empathy=empathy,
            humor=humor,
            advice_level=advice_level,
            intimacy_level=rel_behavior["intimacy_level"],
            energy=energy,
            communication_style=style,
            behavioral_guidance="\n".join(guidelines)
        )
