from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.context.providers.base import ContextProvider
from app.services.character.character_service import CharacterService
from app.services.character.personality_prompt_compiler import PersonalityPromptCompiler
from app.services.character.character_state_resolver import CharacterStateResolver
from app.services.character.response_strategy_resolver import ResponseStrategyResolver

class CharacterIdentityProvider(ContextProvider):
    """
    LEVEL 2 Context Provider:
    Injects persistent Character Identity, Personality DNA, Values, Boundaries, and Agency Strategy.
    """
    def __init__(self, db: Optional[AsyncSession] = None, companion_id: str = "default_companion"):
        self.db = db
        self.companion_id = companion_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, Any]]:
        if not self.db:
            return []

        char_svc = CharacterService(self.db)
        char_data = await char_svc.get_or_create_character(self.companion_id)

        identity = char_data["identity"]
        personality = char_data["personality"]
        values = char_data["values"]
        preferences = char_data["preferences"]
        boundaries = char_data["boundaries"]

        # Resolve Agency Response Strategy
        strategy = ResponseStrategyResolver.resolve_strategy(
            user_input=current_user_message,
            values=values,
            boundaries=boundaries
        )

        # Resolve Current Situational Character State
        state = CharacterStateResolver.resolve(
            companion_id=self.companion_id,
            personality=personality,
            strategy=strategy
        )

        # Resolve Real-time Behavior Instruction (Sprint 33)
        from app.services.character.behavior_resolver import CharacterBehaviorResolver
        behavior_instruction = CharacterBehaviorResolver.resolve_behavior(
            user_input=current_user_message,
            character_state=state,
            character_identity=identity
        )

        # Compile structured prompt block
        compiled_prompt = PersonalityPromptCompiler.compile(
            identity=identity,
            personality=personality,
            values=values,
            preferences=preferences,
            boundaries=boundaries,
            character_state=state,
            strategy=strategy
        )

        # Resolve Dynamic Behavior Directive (Sprint 34)
        from app.services.personality.engines.behavior_engine import PersonalityBehaviorEngine
        directive = PersonalityBehaviorEngine.resolve_behavior(
            user_input=current_user_message
        )

        if behavior_instruction.behavioral_guidance:
            compiled_prompt += f"\n\n[BEHAVIORAL DIRECTIVES & COMMUNICATION STYLE]\n{behavior_instruction.behavioral_guidance}"

        compiled_prompt += (
            f"\n\n[DYNAMIC BEHAVIOR DIRECTIVE]\n"
            f"- Response Style: Warmth={directive.response_style.warmth:.2f}, Humor={directive.response_style.humor:.2f}, Playfulness={directive.response_style.playfulness:.2f}\n"
            f"- Interaction Behavior: Tease={directive.interaction_behavior.tease_user}, ShowConcern={directive.interaction_behavior.show_concern}, AskFollowup={directive.interaction_behavior.ask_followup}\n"
            f"- Emotional Expression: {directive.emotional_expression.expression} (Intensity={directive.emotional_expression.intensity:.2f})\n"
            f"INSTRUCTION: Express this dynamic behavior naturally in your tone, wording, and emotional warmth."
        )

        return [{
            "role": "system",
            "content": compiled_prompt
        }]


