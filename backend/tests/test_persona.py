import pytest
import asyncio
from app.db.models.persona import Persona
from app.services.context.providers.persona_provider import PersonaContextProvider

# Mock PersonaService for testing provider
class MockPersonaService:
    async def get_or_create_persona(self, user_id: str):
        persona = Persona(
            id="test_persona_id",
            companion_id="test_companion_id",
            name="Test Companion",
            personality={"warm": 85, "direct": 10},
            communication_style={"tone": "friendly"},
            values={"empathy": 100},
            behavior_rules=["Never lie."],
            boundaries=["I am an AI."],
            version=1
        )
        return persona

@pytest.mark.asyncio
async def test_persona_context_provider():
    service = MockPersonaService()
    provider = PersonaContextProvider(persona_service=service, user_id="test_user")
    
    context = await provider.build_context("test_conv", "hello")
    
    assert len(context) == 1
    assert context[0]["role"] == "system"
    assert "TRUSTED APPLICATION CONTEXT: PERSONA" in context[0]["content"]
    assert "Name: Test Companion" in context[0]["content"]
    
    # Semantic mapping test
    # warm: 85 -> very high
    assert "warm: very high" in context[0]["content"]
    # direct: 10 -> very low
    assert "direct: very low" in context[0]["content"]
    
    assert "Never lie." in context[0]["content"]
    assert "I am an AI." in context[0]["content"]
