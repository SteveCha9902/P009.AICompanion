import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.vision.adapters.mock_vision_adapter import MockVisionProvider
from app.services.vision.adapters.cloud_vision_adapter import CloudVisionProvider
from app.services.vision_service import VisionService
from app.services.providers.factory import ProviderFactory
from app.db.models.vision import VisionSession, VisionSessionStatus, VisionObservation
from app.services.context.providers.vision_context import VisionContextProvider
from app.services.context.builder import ContextBuilder
from app.db.models.conversation import Conversation
from app.services.llm.base import LLMAuthError

# --- 1. CloudVisionProvider Unit Tests (VISION-3) ---

@pytest.mark.asyncio
async def test_vision_3_cloud_provider_empty_and_auth():
    # Empty image check
    provider = CloudVisionProvider(api_key="sk-test-key")
    res = await provider.analyze_frame(b"")
    assert res["user_visible"] is False
    assert res["confidence"] == 0.0

    # Missing API Key check
    provider_no_key = CloudVisionProvider(api_key="")
    with pytest.raises(LLMAuthError):
        await provider_no_key.analyze_frame(b"image-bytes")


# --- 2. ProviderFactory Vision Selection (VISION-9) ---

def test_vision_9_provider_factory_selection():
    mock_p = ProviderFactory.get_vision_provider("mock")
    assert isinstance(mock_p, MockVisionProvider)

    cloud_p = ProviderFactory.get_vision_provider("cloud")
    assert isinstance(cloud_p, CloudVisionProvider)


# --- 3. Vision Observation & Deduplication (VISION-4) ---

@pytest.mark.asyncio
async def test_vision_4_process_frame_and_deduplication():
    mock_db = MagicMock()
    session_obj = VisionSession(
        id="v-session-001",
        companion_id="comp_1",
        status=VisionSessionStatus.CAMERA_ACTIVE.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = session_obj
    
    # Mock Provider
    mock_provider = AsyncMock()
    mock_provider.analyze_frame.return_value = {
        "user_visible": True,
        "face_detected": True,
        "confidence": 0.92,
        "gaze": "toward_camera",
        "expression": "smiling",
        "objects": ["laptop", "coffee_cup"]
    }

    # First frame has no previous obs
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    vision_service = VisionService(db=mock_db, provider=mock_provider)
    obs = await vision_service.process_frame("v-session-001", b"FRAME-1")

    assert obs.observation_type == "FACE_DETECTED"
    assert obs.confidence == 0.92
    assert session_obj.status == VisionSessionStatus.VISION_READY.value


# --- 4. VisionContextProvider & Trust Boundary (VISION-5 & VISION-6) ---

@pytest.mark.asyncio
async def test_vision_5_6_context_provider_trust_boundary():
    mock_db = MagicMock()
    
    # Conversation
    conv_obj = Conversation(id="conv_vision_1", user_id="user_1")
    conv_obj.companion_id = "comp_1"
    
    # Active session
    session_obj = VisionSession(
        id="v-session-002",
        companion_id="comp_1",
        status=VisionSessionStatus.VISION_READY.value
    )
    
    # High confidence observation
    obs_obj = VisionObservation(
        id="obs-001",
        session_id="v-session-002",
        observation_type="FACE_DETECTED",
        confidence=0.88,
        data={
            "gaze": "toward_camera",
            "expression": "smiling",
            "objects": ["book", "desk"]
        }
    )

    def mock_query(model):
        q = MagicMock()
        if model == Conversation:
            q.filter.return_value.first.return_value = conv_obj
        elif model == VisionSession:
            q.filter.return_value.order_by.return_value.first.return_value = session_obj
        elif model == VisionObservation:
            q.filter.return_value.order_by.return_value.first.return_value = obs_obj
        return q

    mock_db.query.side_effect = mock_query

    vision_ctx_provider = VisionContextProvider(db=mock_db)
    
    # Build full context via ContextBuilder
    builder = ContextBuilder(providers=[vision_ctx_provider])
    context = await builder.build("conv_vision_1", "지금 뭐가 보여?")

    # Verify Trust Boundary
    # 1. System Rule at tier 0
    assert "[TRUSTED SYSTEM & SAFETY RULES]" in context[0]["content"]
    
    # 2. Application Context contains Vision as [CURRENT VISUAL CONTEXT]
    app_ctx = context[1]["content"]
    assert "[CURRENT VISUAL CONTEXT]" in app_ctx
    assert "FACE_DETECTED: 전면 카메라 시각 인지 활성화 상태" in app_ctx
    assert "사용자 착용 의상" in app_ctx
    assert "[CRITICAL MANDATE - REAL-TIME SIGHT]" in app_ctx

    # 3. User Input quarantined at end
    assert context[-1]["role"] == "user"
    assert "[UNTRUSTED USER INPUT]\n지금 뭐가 보여?" in context[-1]["content"]


# --- 5. Vision Failure Isolation (VISION-8) ---

@pytest.mark.asyncio
async def test_vision_8_failure_isolation():
    mock_db = MagicMock()
    session_obj = VisionSession(
        id="v-session-003",
        companion_id="comp_1",
        status=VisionSessionStatus.CAMERA_ACTIVE.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = session_obj

    failing_provider = AsyncMock()
    failing_provider.analyze_frame.side_effect = Exception("Cloud Vision API Unreachable")

    vision_service = VisionService(db=mock_db, provider=failing_provider)

    with pytest.raises(Exception, match="Cloud Vision API Unreachable"):
        await vision_service.process_frame("v-session-003", b"CORRUPTED-FRAME")

    assert session_obj.status == VisionSessionStatus.VISION_ERROR.value
