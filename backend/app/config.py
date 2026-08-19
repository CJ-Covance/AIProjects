from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./atlas.db"
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k_chunks: int = 8
    cors_origins: str = "http://localhost:3000"
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_default_project_key: str = ""

    class Config:
        env_file = ".env"

    @property
    def jira_configured(self) -> bool:
        return bool(self.jira_base_url and self.jira_email and self.jira_api_token)


settings = Settings()
