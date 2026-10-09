import pytest
import os
from unittest.mock import patch
from app.services.providers.factory import ProviderFactory, MockLLMProvider
from app.services.llm.openai import OpenAIProvider
from app.services.voice.adapters.mock_stt_adapter import MockSTTProvider
from app.services.voice.adapters.openai_adapter import OpenAI_STTProvider
from app.services.vision.adapters.mock_vision_adapter import MockVisionProvider
from app.services.vision.adapters.cloud_vision_adapter import CloudVisionProvider

# --- 1. Environment & Provider Configuration Hardening (Gate 1 & 11) ---

def test_gate_1_environment_provider_matrix():
    # Dev mode: all mock
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "mock",
        "STT_PROVIDER": "mock",
        "TTS_PROVIDER": "mock",
        "VISION_PROVIDER": "mock"
    }):
        assert isinstance(ProviderFactory.get_llm_provider(), MockLLMProvider)
        assert isinstance(ProviderFactory.get_stt_provider(), MockSTTProvider)
        assert isinstance(ProviderFactory.get_vision_provider(), MockVisionProvider)

    # Prod mode: all real
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "openai",
        "STT_PROVIDER": "openai",
        "TTS_PROVIDER": "openai",
        "VISION_PROVIDER": "cloud",
        "OPENAI_API_KEY": "sk-production-test-key"
    }):
        assert isinstance(ProviderFactory.get_llm_provider(), OpenAIProvider)
        assert isinstance(ProviderFactory.get_stt_provider(), OpenAI_STTProvider)
        assert isinstance(ProviderFactory.get_vision_provider(), CloudVisionProvider)


# --- 2. Security & No Secret Leaks (Gate 11) ---

def test_gate_11_api_key_isolation_in_exceptions():
    # Ensure error strings never dump raw API key
    secret_key = "sk-super-secret-production-key-999"
    provider = OpenAIProvider(api_key=secret_key)
    
    # Check that string representation of provider doesn't reveal secret key
    assert secret_key not in str(provider)
    assert secret_key not in repr(provider)
