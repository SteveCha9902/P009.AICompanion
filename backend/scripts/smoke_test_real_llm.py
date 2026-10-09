"""
P009.AICompanion - Real OpenAI Smoke Test Script
Usage:
    export OPENAI_API_KEY="your-real-key"
    python scripts/smoke_test_real_llm.py
"""
import asyncio
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.llm.openai import OpenAIProvider
from app.services.companion.domain import NormalizedInput, SSEEventType
from app.services.companion.runtime import create_companion_orchestrator
from unittest.mock import AsyncMock

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[!] OPENAI_API_KEY environment variable is not set. Aborting real smoke test.")
        sys.exit(1)

    print(f"[*] Starting Real OpenAI Smoke Test with model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    
    real_provider = OpenAIProvider()
    mock_db = AsyncMock()
    
    orchestrator = await create_companion_orchestrator(
        db=mock_db,
        user_id="smoke_user",
        companion_id="smoke_companion",
        llm_provider=real_provider
    )

    user_input = NormalizedInput(
        interaction_id=f"INT-SMOKE-{int(asyncio.get_event_loop().time())}",
        user_id="smoke_user",
        companion_id="smoke_companion",
        content="안녕! 오늘 기분이 어때?"
    )

    print("[*] Dispatching Interaction...")
    stream = orchestrator.process_interaction(user_input)
    
    async for sse_chunk in stream:
        for line in sse_chunk.strip().split("\n"):
            if line.startswith("event:"):
                print(f"\n[EVENT] {line}")
            elif line.startswith("data:"):
                print(f"[DATA]  {line[:120]}..." if len(line) > 120 else f"[DATA]  {line}")

    print("\n[✓] Smoke test completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
