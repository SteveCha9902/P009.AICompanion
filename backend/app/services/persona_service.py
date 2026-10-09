import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.companion_repository import CompanionRepository
from app.repositories.persona_repository import PersonaRepository
from app.db.models.persona import Persona

class PersonaService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.companion_repo = CompanionRepository(session)
        self.persona_repo = PersonaRepository(session)

    async def get_or_create_persona(self, user_id: str) -> Persona:
        companion = await self.companion_repo.get_by_user_id(user_id)
        if not companion:
            companion = await self.companion_repo.create(user_id=user_id)
        
        persona = await self.persona_repo.get_by_companion_id(companion.id)
        if not persona:
            # Load default balanced preset
            preset = self.get_preset("balanced")
            persona = await self.persona_repo.create(companion_id=companion.id, **preset)
            
        return persona

    async def update_persona(self, user_id: str, updates: dict) -> Persona:
        persona = await self.get_or_create_persona(user_id)
        # Filter allowed updates to avoid overwriting id, etc.
        allowed = {"name", "personality", "communication_style", "values", "behavior_rules", "boundaries"}
        filtered_updates = {k: v for k, v in updates.items() if k in allowed}
        return await self.persona_repo.update(persona, **filtered_updates)

    async def apply_preset(self, user_id: str, preset_name: str) -> Persona:
        preset_data = self.get_preset(preset_name)
        return await self.update_persona(user_id, preset_data)

    def get_preset(self, preset_name: str) -> dict:
        presets_dir = os.path.join(os.path.dirname(__file__), "..", "..", "presets")
        filepath = os.path.join(presets_dir, f"{preset_name}.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to hardcoded balanced preset if file is missing
            return {
                "name": "Luna",
                "personality": {"warm": 60, "curious": 70, "calm": 50, "playful": 40, "direct": 50},
                "communication_style": {"tone": "friendly", "verbosity": "medium", "formality": "casual", "humor": "light"},
                "values": {"honesty": 80, "empathy": 90},
                "behavior_rules": [
                    "사용자의 질문을 먼저 이해한다.",
                    "불확실하면 추측하지 않는다."
                ],
                "boundaries": [
                    "나는 지나치게 공격적인 표현을 선호하지 않는다."
                ]
            }
