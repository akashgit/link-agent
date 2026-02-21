from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://linkagent:linkagent@localhost:5432/linkagent"
    checkpoint_database_url: str = "postgresql://linkagent:linkagent@localhost:5432/linkagent"
    claude_model: str = "sonnet"
    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
