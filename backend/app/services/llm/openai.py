import os
import logging
from typing import List, Optional, AsyncGenerator, Dict, Any
from app.services.llm.base import (
    BaseLLMProvider, 
    LLMResponse, 
    LLMProviderError, 
    LLMAuthError, 
    LLMRateLimitError, 
    LLMTimeoutError, 
    LLMConfigError
)

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    """
    Production-grade OpenAI LLM Provider Adapter.
    Encapsulates OpenAI SDK dependencies, timeout, streaming, and error mapping.
    """
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 timeout_seconds: Optional[float] = None,
                 max_tokens: Optional[int] = None):
        if AsyncOpenAI is None:
            raise LLMConfigError("OpenAI SDK is not installed. Please install openai package.")

        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_seconds = timeout_seconds or float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20.0"))
        self.max_tokens = max_tokens or int(os.getenv("OPENAI_MAX_TOKENS", "1024"))

        if not self.api_key:
            logger.warning("[OpenAIProvider] OPENAI_API_KEY is not configured.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

    def _ensure_client(self):
        if not self.client:
            raise LLMAuthError("OPENAI_API_KEY is missing or empty. Please set OPENAI_API_KEY.")

    async def generate(self, messages: List[dict]) -> LLMResponse:
        self._ensure_client()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            choice = response.choices[0]
            usage_dict = response.usage.model_dump() if response.usage else {}
            
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                usage=usage_dict,
                finish_reason=choice.finish_reason
            )
        except openai.AuthenticationError as e:
            logger.error(f"[OpenAIProvider] Authentication failed: {e}")
            raise LLMAuthError(f"OpenAI Authentication Error: {e}", original_error=e)
        except openai.RateLimitError as e:
            logger.error(f"[OpenAIProvider] Rate limit exceeded: {e}")
            raise LLMRateLimitError(f"OpenAI Rate Limit Exceeded: {e}", original_error=e)
        except (openai.APITimeoutError, TimeoutError) as e:
            logger.error(f"[OpenAIProvider] Request timed out: {e}")
            raise LLMTimeoutError(f"OpenAI API Timeout: {e}", original_error=e)
        except openai.APIConnectionError as e:
            logger.error(f"[OpenAIProvider] Connection failed: {e}")
            raise LLMProviderError(f"OpenAI Connection Failed: {e}", code="PROVIDER_NETWORK_ERROR", original_error=e)
        except Exception as e:
            logger.error(f"[OpenAIProvider] Unexpected error: {e}")
            raise LLMProviderError(f"OpenAI Provider Error: {e}", code="PROVIDER_ERROR", original_error=e)

    async def stream(self, messages: List[dict]) -> AsyncGenerator[LLMResponse, None]:
        self._ensure_client()
        try:
            stream_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7,
                stream=True
            )
            async for chunk in stream_response:
                if len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    content = delta.content or ""
                    finish_reason = chunk.choices[0].finish_reason
                    if content or finish_reason:
                        yield LLMResponse(
                            content=content,
                            model=chunk.model or self.model,
                            finish_reason=finish_reason
                        )
        except openai.AuthenticationError as e:
            logger.error(f"[OpenAIProvider] Authentication failed in stream: {e}")
            raise LLMAuthError(f"OpenAI Authentication Error: {e}", original_error=e)
        except openai.RateLimitError as e:
            logger.error(f"[OpenAIProvider] Rate limit exceeded in stream: {e}")
            raise LLMRateLimitError(f"OpenAI Rate Limit Exceeded: {e}", original_error=e)
        except (openai.APITimeoutError, TimeoutError) as e:
            logger.error(f"[OpenAIProvider] Stream timed out: {e}")
            raise LLMTimeoutError(f"OpenAI API Stream Timeout: {e}", original_error=e)
        except openai.APIConnectionError as e:
            logger.error(f"[OpenAIProvider] Stream connection failed: {e}")
            raise LLMProviderError(f"OpenAI Connection Failed: {e}", code="PROVIDER_NETWORK_ERROR", original_error=e)
        except Exception as e:
            logger.error(f"[OpenAIProvider] Unexpected error in stream: {e}")
            raise LLMProviderError(f"OpenAI Provider Stream Error: {e}", code="PROVIDER_ERROR", original_error=e)
