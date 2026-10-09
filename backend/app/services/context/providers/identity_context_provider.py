from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.services.identity.identity_continuity_engine import IdentityContinuityEngine

class IdentityContextProvider(ContextProvider):
    """
    Identity Continuity & Multi-Year Relationship Context Provider:
    Injects longitudinal identity anchors, life chapters, and reminiscing guidance into ContextBuilder.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        rem_res = IdentityContinuityEngine.generate_reminiscing_guidance(
            user_id=self.user_id,
            user_utterance=current_user_message
        )

        snap = IdentityContinuityEngine.get_snapshot(self.user_id)
        parts = []

        if snap.core_interests or snap.life_stage:
            interests_str = ", ".join(snap.core_interests) if snap.core_interests else "다양한 관심사"
            parts.append(f"User Core Identity: {snap.life_stage} (Interests: {interests_str})")

        if rem_res:
            intent_name, chapter_title, guidance = rem_res
            parts.append(f"[{intent_name}: Chapter '{chapter_title}']\n{guidance}")

        if not parts:
            return []

        return [{
            "role": "system",
            "content": "\n[MULTI-YEAR IDENTITY & SHARED ODYSSEY]\n" + "\n".join(parts)
        }]
