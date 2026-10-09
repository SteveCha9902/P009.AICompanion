import asyncio
from typing import AsyncGenerator
from app.services.voice.stt_provider_interface import BaseSTTProvider

class MockSTTProvider(BaseSTTProvider):
    async def transcribe(self, audio_data: bytes) -> str:
        """Simulate transcription of audio data."""
        await asyncio.sleep(0.5)  # Simulate network latency
        return "[Mock STT] 지난번에 이야기했던 카메라 말인데..."

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Simulate streaming transcription."""
        async for _ in audio_stream:
            await asyncio.sleep(0.1)
            yield "[Mock Streaming STT Result] "
