from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ENV_FILE, settings
from app.database import Base, engine
from app.middleware.activity_logging import ActivityLoggingMiddleware, register_exception_handlers
from app.migrate import run_migrations
from app.routers import domains, logs, pages, projects, search, sources


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    yield


app = FastAPI(
    title="Atlas — Unified Knowledge Platform",
    description="Enterprise knowledge platform with RAG-powered search",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
# Ensure common local dev origins work on Windows
for extra in ("http://127.0.0.1:3000", "http://localhost:3000"):
    if extra not in origins:
        origins.append(extra)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ActivityLoggingMiddleware)
register_exception_handlers(app)

app.include_router(sources.router)
app.include_router(domains.router)
app.include_router(projects.router)
app.include_router(pages.router)
app.include_router(search.router)
app.include_router(logs.router)


@app.get("/api/health")
def health():
    from app.services.activity_log import LOG_FILE
    from app.services.llm_provider import (
        get_embedding_provider_name,
        is_ai_configured,
        is_google_configured,
        is_openai_configured,
    )

    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "embedding_provider": get_embedding_provider_name(),
        "openai_configured": is_openai_configured(),
        "google_configured": is_google_configured(),
        "ai_configured": is_ai_configured(),
        "env_file": str(ENV_FILE),
        "env_file_exists": ENV_FILE.exists(),
        "log_file": str(LOG_FILE),
        "api_base_hint": "http://localhost:8000",
    }
