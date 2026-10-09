import asyncio
from app.services.context.builder import ContextBuilder
from app.services.character.context_resolver import CharacterContextResolver

async def main():
    cr = CharacterContextResolver()
    
    # 1. Resolve Mani
    ctx_mani = await cr.resolve("default_user", "c_mani")
    cb = ContextBuilder([])
    prompt_mani = await cb.build("conv_mani", "마니야 안녕?", "c_mani", ctx_mani)
    print("=== MANI SYSTEM PROMPT (LEVEL 1) ===")
    print(prompt_mani[0]["content"][:400])

    # 2. Resolve Genie
    ctx_genie = await cr.resolve("default_user", "default_companion")
    prompt_genie = await cb.build("conv_genie", "여보 안녕?", "default_companion", ctx_genie)
    print("\n=== GENIE SYSTEM PROMPT (LEVEL 1) ===")
    print(prompt_genie[0]["content"][:400])

asyncio.run(main())
