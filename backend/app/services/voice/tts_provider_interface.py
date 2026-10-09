from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseTTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice_context: dict = None) -> bytes:
        """Synthesize text into audio data."""
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str, voice_context: dict = None) -> AsyncGenerator[bytes, None]:
        """Synthesize text into streaming audio data."""
        pass
