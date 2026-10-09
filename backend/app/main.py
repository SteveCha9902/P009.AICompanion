from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import (
    companion,
    voice,
    vision,
    avatar,
    conversations,
    personas,
    memories,
    emotions,
    relationships,
    presence,
    proactive,
    notifications,
    character,
    characters,
    memory_timeline,
    reflections
)


from app.services.companion.runtime import runtime_lifecycle
from app.db.base import Base
from sqlalchemy import text
from app.db.session import engine, async_session

@asynccontextmanager

async def lifespan(app: FastAPI):
    # Startup Lifecycle: Ensure database tables are created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure default user, test_user_1, and companion exist
    try:
        async with async_session() as session:
            await session.execute(text("""
                INSERT INTO users (id, external_id)
                VALUES ('default_user', 'ext_default_user')
                ON CONFLICT (id) DO NOTHING;
            """))
            await session.execute(text("""
                INSERT INTO users (id, external_id)
                VALUES ('test_user_1', 'ext_test_user_1')
                ON CONFLICT (id) DO NOTHING;
            """))
            await session.execute(text("""
                INSERT INTO companions (id, user_id, name)
                VALUES ('default_companion', 'default_user', 'Genie')
                ON CONFLICT (id) DO NOTHING;
            """))
            await session.commit()
    except Exception as e:
        pass


    runtime_lifecycle.initialize()
    runtime_lifecycle.start()
    yield
    # Shutdown Lifecycle
    runtime_lifecycle.stop()



app = FastAPI(
    title="P009.AICompanion Cognitive Runtime API",
    description="Unified Interaction Engine API connecting Cognitive Core, Voice, Vision, and Avatar presentation.",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS to allow mobile client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Primary Unified Interaction Entrypoint & Multimodal Routers
app.include_router(companion.router, prefix="/api/v1")
app.include_router(voice.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")
app.include_router(avatar.router, prefix="/api/v1")

# 2. Cognitive Domain Routers
app.include_router(character.router, prefix="/api/v1")
app.include_router(characters.router, prefix="/api/v1")
app.include_router(memory_timeline.router, prefix="/api/v1")
app.include_router(reflections.router, prefix="/api/v1")
app.include_router(personas.router, prefix="/api/v1")


app.include_router(memories.router, prefix="/api/v1")
app.include_router(emotions.router, prefix="/api/v1")

app.include_router(relationships.router, prefix="/api/v1")
app.include_router(presence.router, prefix="/api/v1")
app.include_router(proactive.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

# 3. Legacy Routers (Isolated)
app.include_router(conversations.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """Liveness probe: verifies process alive."""
    return {
        "status": "ok", 
        "runtime_state": runtime_lifecycle.state.value,
        "message": "P009 Cognitive Runtime is active",
        "orchestrator_entrypoint": "/api/v1/companion/interactions"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe: verifies database and core subsystems are initialized."""
    db_ok = True
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "ready" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "runtime_state": runtime_lifecycle.state.value,
        "orchestrator_ready": True
    }

