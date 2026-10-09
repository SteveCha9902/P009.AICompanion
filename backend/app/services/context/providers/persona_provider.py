from typing import List
from app.services.context.providers.base import ContextProvider
from app.services.persona_service import PersonaService
from app.db.models.persona import Persona

class PersonaContextProvider(ContextProvider):
    def __init__(self, persona_service: PersonaService, user_id: str, companion_id: str = "default_companion"):
        self.persona_service = persona_service
        self.user_id = user_id
        self.companion_id = companion_id

    def _map_score_to_semantic(self, score: int) -> str:
        if score <= 20:
            return "very low"
        elif score <= 40:
            return "low"
        elif score <= 60:
            return "moderate"
        elif score <= 80:
            return "high"
        else:
            return "very high"

    def _format_persona(self, persona: Persona) -> str:
        lines = [f"Name: {persona.name}"]
        
        lines.append("\nPersonality Traits:")
        for trait, score in persona.personality.items():
            semantic_level = self._map_score_to_semantic(score)
            lines.append(f"- {trait}: {semantic_level}")

        lines.append("\nCommunication Style:")
        for key, val in persona.communication_style.items():
            lines.append(f"- {key}: {val}")

        lines.append("\nValues:")
        for val_k, val_v in persona.values.items():
            lines.append(f"- {val_k}: {self._map_score_to_semantic(val_v) if isinstance(val_v, int) else val_v}")

        if persona.behavior_rules:
            lines.append("\nBehavior Tendencies:")
            for rule in persona.behavior_rules:
                lines.append(f"- {rule}")
        
        if persona.boundaries:
            lines.append("\nBoundaries (Realism and Safety):")
            # Enforce the realism boundary explicitly
            lines.append("- DO NOT claim physical existence in the real world.")
            lines.append("- DO NOT fabricate false physical memories (e.g. going for a walk in reality).")
            for boundary in persona.boundaries:
                lines.append(f"- {boundary}")

        return "\n".join(lines)

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        cid = getattr(self, "companion_id", "default_companion")
        cid_lower = (cid or "").lower()
        # In multi-character system, CharacterIdentityProvider (Level 2) and ContextBuilder (Level 1)
        # govern personas. Skip old spousal Luna persona for other characters.
        if "mani" in cid_lower or "마니" in cid or "hana" in cid_lower or "하나" in cid or (cid != "default_companion" and "genie" not in cid_lower):
            return []

        persona = await self.persona_service.get_or_create_persona(self.user_id)
        formatted_persona = self._format_persona(persona)
        
        return [
            {
                "role": "system",
                "content": f"[TRUSTED APPLICATION CONTEXT: PERSONA]\n{formatted_persona}"
            }
        ]
