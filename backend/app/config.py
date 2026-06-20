from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always load .env from the backend folder, even if uvicorn is started elsewhere
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./atlas.db"
    knowledge_base_root: str = "knowledge_base"
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k_chunks: int = 8
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
