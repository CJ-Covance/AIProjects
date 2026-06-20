from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import domains, pages, projects, search, sources


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Atlas — Unified Knowledge Platform",
    description="Enterprise knowledge platform with RAG-powered search",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router)
app.include_router(domains.router)
app.include_router(projects.router)
app.include_router(pages.router)
app.include_router(search.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "openai_configured": bool(settings.openai_api_key),
    }
