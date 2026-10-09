from typing import List, Optional, AsyncGenerator, Dict, Any
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Standard Error Domain for LLM Providers
class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""
    def __init__(self, message: str, code: str = "PROVIDER_ERROR", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.original_error = original_error

class LLMAuthError(LLMProviderError):
    """Raised when authentication with the LLM provider fails."""
    def __init__(self, message: str = "LLM authentication failed. Check API key.", original_error: Optional[Exception] = None):
        super().__init__(message, code="PROVIDER_AUTH_ERROR", original_error=original_error)

class LLMRateLimitError(LLMProviderError):
    """Raised when LLM provider rate limit is exceeded."""
    def __init__(self, message: str = "LLM rate limit exceeded. Please retry later.", original_error: Optional[Exception] = None):
        super().__init__(message, code="PROVIDER_RATE_LIMIT", original_error=original_error)

class LLMTimeoutError(LLMProviderError):
    """Raised when LLM provider request times out."""
    def __init__(self, message: str = "LLM request timed out.", original_error: Optional[Exception] = None):
        super().__init__(message, code="PROVIDER_TIMEOUT", original_error=original_error)

class LLMConfigError(LLMProviderError):
    """Raised when LLM provider configuration is invalid or missing."""
    def __init__(self, message: str = "Invalid LLM provider configuration.", original_error: Optional[Exception] = None):
        super().__init__(message, code="PROVIDER_CONFIG_ERROR", original_error=original_error)

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[dict]) -> LLMResponse:
        pass

    @abstractmethod
    async def stream(self, messages: List[dict]) -> AsyncGenerator[LLMResponse, None]:
        pass
