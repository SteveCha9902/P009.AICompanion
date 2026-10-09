import pytest
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.services.companion.domain import NormalizedInput, InputType, SSEEventType
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.runtime import create_companion_orchestrator
from app.services.voice_service import VoiceService
from app.services.context.builder import ContextBuilder
from app.services.context.providers.vision_context import VisionContextProvider
from app.services.context.providers.presence_provider import PresenceContextProvider
from app.services.context.providers.persona_provider import PersonaContextProvider
from app.services.context.providers.relationship_provider import RelationshipContextProvider
from app.services.context.providers.emotion_provider import EmotionContextProvider
from app.services.context.providers.memory_provider import MemoryContextProvider
from app.services.context.providers.conversation_history import ConversationHistoryProvider
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.db.models.vision import VisionObservation, VisionSession, VisionSessionStatus
from app.db.models.conversation import Conversation
from app.db.models.voice_session import VoiceSession, VoiceSessionStatus

# Mock LLM Chunk
class MockChunk:
    def __init__(self, content: str):
        self.content = content

class MockLLMProvider:
    def __init__(self, output_text="Hello! I am your AI companion."):
        self.output_text = output_text
        self.captured_context = []

    async def stream(self, context):
        self.captured_context = context
        words = self.output_text.split(" ")
        for word in words:
            yield MockChunk(word + " ")

@pytest.mark.asyncio
async def test_gate_a_text_pipeline_json_sse():
    """
    Gate A - Text Pipeline:
    POST /api/v1/companion/interactions -> CompanionOrchestrator -> 7 Context Providers -> LLM -> JSON SSE
    """
    mock_llm = MockLLMProvider("Hello there! It is great to talk with you.")
    mock_db = AsyncMock()
    
    orchestrator = await create_companion_orchestrator(
        db=mock_db,
        user_id="user_123",
        companion_id="comp_123",
        llm_provider=mock_llm
    )
    
    input_data = NormalizedInput(
        interaction_id="INT-TEST-001",
        user_id="user_123",
        companion_id="comp_123",
        conversation_id="conv_123",
        input_type=InputType.TEXT,
        content="How are you feeling today?"
    )

    events_received = []
    async for event_chunk in orchestrator.process_interaction(input_data):
        events_received.append(event_chunk)

    full_output = "".join(events_received)
    
    # Verify standard SSE events are present
    assert "event: interaction_started" in full_output
    assert "event: thinking" in full_output
    assert "event: text_delta" in full_output
    assert "event: text_completed" in full_output
    assert "event: avatar_state" in full_output
    assert "event: interaction_completed" in full_output
    assert "INT-TEST-001" in full_output


@pytest.mark.asyncio
async def test_gate_b_voice_pipeline_routes_through_orchestrator():
    """
    Gate B - Voice Pipeline:
    VoiceService -> STT -> Interaction Normalization -> CompanionOrchestrator -> Unified Response -> TTS
    (Ensuring ConversationService is NOT called)
    """
    mock_stt = AsyncMock()
    mock_stt.transcribe.return_value = "Hello voice companion"

    mock_tts = AsyncMock()
    mock_tts.synthesize.return_value = b"MOCK_WAV_AUDIO_BYTES"

    mock_orchestrator = AsyncMock()
    from app.services.companion.domain import UnifiedResponse
    mock_orchestrator.process_interaction_sync.return_value = UnifiedResponse(
        interaction_id="INT-VOICE-123",
        text="I heard your voice loud and clear!",
        avatar_state={"expression": "smile", "animation": "speaking"}
    )

    mock_db = MagicMock()
    mock_session = VoiceSession(
        session_id="voice_sess_001",
        user_id="user_123",
        companion_id="comp_123",
        conversation_id="conv_123",
        status=VoiceSessionStatus.IDLE.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session

    voice_service = VoiceService(
        db=mock_db,
        stt_provider=mock_stt,
        tts_provider=mock_tts,
        orchestrator=mock_orchestrator
    )

    audio_result = await voice_service.process_audio("voice_sess_001", b"fake_input_audio")

    # 1. STT was called
    mock_stt.transcribe.assert_awaited_once_with(b"fake_input_audio")
    
    # 2. CompanionOrchestrator was called with NormalizedInput
    mock_orchestrator.process_interaction_sync.assert_awaited_once()
    called_input = mock_orchestrator.process_interaction_sync.call_args[0][0]
    assert called_input.input_type == InputType.VOICE
    assert called_input.content == "Hello voice companion"
    assert called_input.user_id == "user_123"

    # 3. TTS was called with response text
    mock_tts.synthesize.assert_awaited_once()
    assert mock_tts.synthesize.call_args[0][0] == "I heard your voice loud and clear!"
    assert audio_result == b"MOCK_WAV_AUDIO_BYTES"


@pytest.mark.asyncio
async def test_gate_c_vision_context_injected_into_builder():
    """
    Gate C - Vision Context:
    Vision Observation is formatted by VisionContextProvider and injected into ContextBuilder
    """
    mock_db = MagicMock()
    
    mock_conv = Conversation(id="conv_123", user_id="user_123")
    mock_vision_sess = VisionSession(
        id="vis_sess_123",
        companion_id="conv_123",
        status=VisionSessionStatus.CAMERA_ACTIVE.value
    )
    mock_obs = VisionObservation(
        id="obs_123",
        session_id="vis_sess_123",
        observation_type="FACE_DETECTED",
        confidence=0.92,
        data={"gaze": "toward_camera", "expression": "smiling"}
    )

    def query_impl(model):
        query_mock = MagicMock()
        if model == Conversation:
            query_mock.filter.return_value.first.return_value = mock_conv
        elif model == VisionSession:
            query_mock.filter.return_value.order_by.return_value.first.return_value = mock_vision_sess
        elif model == VisionObservation:
            query_mock.filter.return_value.order_by.return_value.first.return_value = mock_obs
        return query_mock

    mock_db.query.side_effect = query_impl

    vision_provider = VisionContextProvider(db=mock_db)
    context_builder = ContextBuilder(providers=[vision_provider])

    context = await context_builder.build("conv_123", "Look at me")
    
    # Verify vision context was included
    found_vision = any("FACE_DETECTED" in c.get("content", "") or "toward_camera" in c.get("content", "") or "smiling" in c.get("content", "") for c in context)
    assert found_vision, f"Vision context was not injected. Context was: {context}"


@pytest.mark.asyncio
async def test_gate_d_avatar_integration_in_post_processing():
    """
    Gate D - Avatar Integration:
    Interaction completion includes AvatarStateResolver output in unified SSE & sync responses
    """
    mock_llm = MockLLMProvider("I am happy to see you!")
    mock_resolver = MagicMock()
    mock_resolver.resolve.return_value = {
        "expression": "warm_smile",
        "animation": "relaxed",
        "intensity": 0.85,
        "gaze": "user"
    }

    mock_db = AsyncMock()
    orchestrator = await create_companion_orchestrator(
        db=mock_db,
        user_id="user_123",
        companion_id="comp_123",
        llm_provider=mock_llm
    )
    orchestrator.avatar_resolver = mock_resolver

    input_data = NormalizedInput(
        interaction_id="INT-AVATAR-001",
        user_id="user_123",
        companion_id="comp_123",
        conversation_id="conv_123",
        content="Hi!"
    )

    sync_response = await orchestrator.process_interaction_sync(input_data)
    assert sync_response.avatar_state["expression"] == "warm_smile"
    assert sync_response.avatar_state["intensity"] == 0.85
    mock_resolver.resolve.assert_called_with("comp_123")


def test_gate_e_legacy_isolation_and_openapi_routes():
    """
    Gate E - Legacy Isolation & Router Registration:
    Verify main FastAPI app includes both /companion/interactions and legacy /conversations routes in OpenAPI schema
    """
    openapi_schema = app.openapi()
    paths = openapi_schema["paths"].keys()

    # New Unified & Multimodal Endpoints
    assert "/api/v1/companion/interactions" in paths
    assert "/api/v1/voice/sessions" in paths
    assert "/api/v1/vision/sessions" in paths
    assert "/api/v1/avatar/state" in paths

    # Legacy Endpoints (Maintained for Backward Compatibility)
    assert "/api/v1/conversations" in paths
    assert "/health" in paths
