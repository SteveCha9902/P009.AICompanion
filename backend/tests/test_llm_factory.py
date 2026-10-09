import pytest
import os
from unittest.mock import patch
from app.services.providers.factory import ProviderFactory, MockLLMProvider
from app.services.llm.openai import OpenAIProvider

def test_provider_factory_mock_default():
    with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
        provider = ProviderFactory.get_llm_provider()
        assert isinstance(provider, MockLLMProvider)

def test_provider_factory_openai_selection():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "sk-dummy"}):
        provider = ProviderFactory.get_llm_provider()
        assert isinstance(provider, OpenAIProvider)

def test_provider_factory_explicit_override():
    provider_mock = ProviderFactory.get_llm_provider("mock")
    assert isinstance(provider_mock, MockLLMProvider)

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-dummy"}):
        provider_real = ProviderFactory.get_llm_provider("openai")
        assert isinstance(provider_real, OpenAIProvider)
