import asyncio
import websockets
import json

async def test():
    uri = "ws://127.0.0.1:8000/api/v1/voice/live-ws"
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "event": "session.start",
            "session_id": "test_s1",
            "user_id": "default_user",
            "companion_id": "default_companion",
            "conversation_id": "default"
        }))
        res = await ws.recv()
        print("Received from server:", res)

if __name__ == "__main__":
    asyncio.run(test())
