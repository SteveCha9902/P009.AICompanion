import asyncio
from typing import AsyncGenerator
from app.services.voice.tts_provider_interface import BaseTTSProvider

class MockTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, voice_context: dict = None) -> bytes:
        """Simulate synthesis of text into audio."""
        await asyncio.sleep(0.5)  # Simulate network latency
        return b"MOCK_AUDIO_DATA_" + text.encode('utf-8')

    async def synthesize_stream(self, text: str, voice_context: dict = None) -> AsyncGenerator[bytes, None]:
        """Simulate streaming synthesis."""
        words = text.split()
        for word in words:
            await asyncio.sleep(0.1)
            yield b"MOCK_AUDIO_CHUNK_" + word.encode('utf-8')
