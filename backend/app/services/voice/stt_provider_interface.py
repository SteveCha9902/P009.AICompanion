from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseSTTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data into text."""
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Transcribe streaming audio data."""
        pass
