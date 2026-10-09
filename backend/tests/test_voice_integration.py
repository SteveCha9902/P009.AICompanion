import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.voice.adapters.mock_stt_adapter import MockSTTProvider
from app.services.voice.adapters.mock_tts_adapter import MockTTSProvider
from app.services.voice.adapters.openai_adapter import OpenAI_STTProvider, OpenAI_TTSProvider
from app.services.voice_service import VoiceService
from app.services.providers.factory import ProviderFactory
from app.db.models.voice_session import VoiceSession, VoiceSessionStatus
from app.services.companion.domain import UnifiedResponse
from app.services.llm.base import LLMAuthError

# --- 1. Real STT & TTS Adapter Tests (Gate V1 & V2) ---

@pytest.mark.asyncio
async def test_gate_v1_stt_adapter_empty_and_auth():
    # Empty audio check
    stt = OpenAI_STTProvider(api_key="sk-test-key")
    res = await stt.transcribe(b"")
    assert res == ""

    # Missing key check
    stt_no_key = OpenAI_STTProvider(api_key="")
    with pytest.raises(LLMAuthError):
        await stt_no_key.transcribe(b"audio-bytes")

@pytest.mark.asyncio
async def test_gate_v2_tts_adapter_empty_and_auth():
    # Empty text check
    tts = OpenAI_TTSProvider(api_key="sk-test-key")
    res = await tts.synthesize("")
    assert res == b""

    # Missing key check
    tts_no_key = OpenAI_TTSProvider(api_key="")
    with pytest.raises(LLMAuthError):
        await tts_no_key.synthesize("Hello")


# --- 2. Provider Factory STT/TTS Selection (Gate V8) ---

def test_gate_v8_provider_factory_voice():
    # Mock Selection
    mock_stt = ProviderFactory.get_stt_provider("mock")
    mock_tts = ProviderFactory.get_tts_provider("mock")
    assert isinstance(mock_stt, MockSTTProvider)
    assert isinstance(mock_tts, MockTTSProvider)

    # OpenAI Selection
    real_stt = ProviderFactory.get_stt_provider("openai")
    real_tts = ProviderFactory.get_tts_provider("openai")
    assert isinstance(real_stt, OpenAI_STTProvider)
    assert isinstance(real_tts, OpenAI_TTSProvider)


# --- 3. Full Voice Pipeline: STT -> Orchestrator -> LLM -> TTS (Gate V3, V4, V5) ---

@pytest.mark.asyncio
async def test_gate_v3_v4_v5_voice_service_full_pipeline():
    mock_db = MagicMock()
    
    # Mock session
    session_obj = VoiceSession(
        session_id="session-test-001",
        user_id="user_1",
        companion_id="comp_1",
        conversation_id="conv_1",
        status=VoiceSessionStatus.IDLE.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = session_obj

    mock_stt = AsyncMock()
    mock_stt.transcribe.return_value = "오늘 기분이 어때?"

    mock_tts = AsyncMock()
    mock_tts.synthesize.return_value = b"RIFF-WAV-AUDIO-BYTES"

    mock_orchestrator = AsyncMock()
    mock_orchestrator.process_interaction_sync.return_value = UnifiedResponse(
        interaction_id="INT-VOICE-001",
        text="오늘 하루도 당신과 함께해서 정말 기뻐요!",
        avatar_state={"expression": "happy", "animation": "nod"}
    )

    voice_service = VoiceService(
        db=mock_db,
        stt_provider=mock_stt,
        tts_provider=mock_tts,
        orchestrator=mock_orchestrator
    )

    # Run Voice Pipeline
    audio_output = await voice_service.process_audio("session-test-001", b"USER-AUDIO-INPUT")

    # Assertions
    assert audio_output == b"RIFF-WAV-AUDIO-BYTES"
    assert mock_stt.transcribe.called
    assert mock_orchestrator.process_interaction_sync.called
    assert mock_tts.synthesize.called
    
    # State transitions ended back in IDLE
    assert session_obj.status == VoiceSessionStatus.IDLE.value


# --- 4. User Interrupt while Speaking (Gate V6) ---

def test_gate_v6_user_interrupt():
    mock_db = MagicMock()
    session_obj = VoiceSession(
        session_id="session-test-002",
        user_id="user_1",
        companion_id="comp_1",
        conversation_id="conv_1",
        status=VoiceSessionStatus.SPEAKING.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = session_obj

    voice_service = VoiceService(
        db=mock_db,
        stt_provider=MockSTTProvider(),
        tts_provider=MockTTSProvider(),
        orchestrator=MagicMock()
    )

    # User interrupts speaking avatar
    voice_service.interrupt_session("session-test-002")

    # State should immediately become LISTENING
    assert session_obj.status == VoiceSessionStatus.LISTENING.value


# --- 5. Failure Isolation & Text Fallback (Gate V7) ---

@pytest.mark.asyncio
async def test_gate_v7_voice_failure_isolation():
    mock_db = MagicMock()
    session_obj = VoiceSession(
        session_id="session-test-003",
        user_id="user_1",
        companion_id="comp_1",
        conversation_id="conv_1",
        status=VoiceSessionStatus.IDLE.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = session_obj

    failing_stt = AsyncMock()
    failing_stt.transcribe.side_effect = Exception("STT Network Down")

    voice_service = VoiceService(
        db=mock_db,
        stt_provider=failing_stt,
        tts_provider=MockTTSProvider(),
        orchestrator=MagicMock()
    )

    # Failure should set session to ERROR without killing process
    with pytest.raises(Exception, match="STT Network Down"):
        await voice_service.process_audio("session-test-003", b"AUDIO")

    assert session_obj.status == VoiceSessionStatus.ERROR.value
    assert "STT Network Down" in session_obj.error_code
