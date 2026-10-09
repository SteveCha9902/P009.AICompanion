import pytest
import asyncio
import json
import base64
from unittest.mock import AsyncMock, MagicMock
from app.services.voice_realtime_channel import VoiceRealtimeSessionHandler

class FakeWebSocket:
    def __init__(self, incoming_messages=None):
        self.accepted = False
        self.closed = False
        self.incoming = list(incoming_messages or [])
        self.sent_events = []

    async def accept(self):
        self.accepted = True

    async def receive_text(self):
        if self.incoming:
            return self.incoming.pop(0)
        # Simulate wait then disconnect
        await asyncio.sleep(0.01)
        from fastapi import WebSocketDisconnect
        raise WebSocketDisconnect()

    async def send_text(self, data: str):
        self.sent_events.append(json.loads(data))

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_realtime_channel_lifecycle_and_handshake():
    """Validates session.start -> session.ready -> ping -> pong -> session.end lifecycle"""
    incoming = [
        json.dumps({
            "event": "session.start",
            "session_id": "test-sess-100",
            "user_id": "user_1",
            "companion_id": "Genie",
            "conversation_id": "conv_1"
        }),
        json.dumps({
            "event": "ping",
            "timestamp": 123456789
        }),
        json.dumps({
            "event": "session.end"
        })
    ]
    ws = FakeWebSocket(incoming)
    stt = AsyncMock()
    tts = AsyncMock()
    orchestrator = MagicMock()

    handler = VoiceRealtimeSessionHandler(
        websocket=ws,
        stt_provider=stt,
        tts_provider=tts,
        orchestrator=orchestrator
    )

    await handler.run()

    assert ws.accepted is True
    event_types = [e.get("event") for e in ws.sent_events]
    assert "session.ready" in event_types
    assert "pong" in event_types
    assert "session.ended" in event_types

    ready_event = next(e for e in ws.sent_events if e.get("event") == "session.ready")
    assert ready_event["user_id"] == "user_1"
    assert ready_event["companion_id"] == "Genie"


@pytest.mark.asyncio
async def test_realtime_channel_audio_turn_streaming():
    """Validates audio.send -> transcript.final -> response.chunk -> audio.chunk -> response.end"""
    dummy_audio_b64 = base64.b64encode(b"FAKE_AUDIO_DATA_FOR_TEST").decode("utf-8")
    incoming = [
        json.dumps({
            "event": "session.start",
            "session_id": "test-sess-200",
            "user_id": "user_2",
            "companion_id": "Genie"
        }),
        json.dumps({
            "event": "audio.send",
            "audio_base64": dummy_audio_b64
        })
    ]
    ws = FakeWebSocket(incoming)

    stt = AsyncMock()
    stt.transcribe.return_value = "안녕 지니야?"

    tts = AsyncMock()
    tts.synthesize.return_value = b"FAKE_SYNTHESIZED_TTS_MP3"

    async def mock_stream_chunks(normalized_input):
        yield "안녕하세요!", False, {"expression": "happy"}, "안녕하세요! 반갑습니다."
        yield "반갑습니다.", True, {"expression": "speaking"}, "안녕하세요! 반갑습니다."

    orchestrator = MagicMock()
    orchestrator.process_interaction_stream_chunks = mock_stream_chunks

    handler = VoiceRealtimeSessionHandler(
        websocket=ws,
        stt_provider=stt,
        tts_provider=tts,
        orchestrator=orchestrator
    )

    await handler.run()

    event_types = [e.get("event") for e in ws.sent_events]
    assert "transcript.start" in event_types
    assert "transcript.final" in event_types
    assert "response.start" in event_types
    assert "response.chunk" in event_types
    assert "audio.chunk" in event_types
    assert "response.end" in event_types

    transcript_event = next(e for e in ws.sent_events if e.get("event") == "transcript.final")
    assert transcript_event["transcript"] == "안녕 지니야?"

    audio_events = [e for e in ws.sent_events if e.get("event") == "audio.chunk"]
    assert len(audio_events) >= 1
    assert audio_events[0]["audio_base64"] != ""


@pytest.mark.asyncio
async def test_realtime_channel_interruption():
    """Validates immediate Barge-in cancellation over WebSocket"""
    incoming = [
        json.dumps({
            "event": "session.start",
            "session_id": "test-sess-300"
        }),
        json.dumps({
            "event": "interruption"
        })
    ]
    ws = FakeWebSocket(incoming)
    stt = AsyncMock()
    tts = AsyncMock()
    orchestrator = MagicMock()

    handler = VoiceRealtimeSessionHandler(
        websocket=ws,
        stt_provider=stt,
        tts_provider=tts,
        orchestrator=orchestrator
    )

    await handler.run()

    event_types = [e.get("event") for e in ws.sent_events]
    assert "interrupted" in event_types
