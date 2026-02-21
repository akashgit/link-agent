from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://linkagent:linkagent@localhost:5432/linkagent"
    checkpoint_database_url: str = "postgresql://linkagent:linkagent@localhost:5432/linkagent"
    claude_model: str = "sonnet"
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    typefully_api_key: str = ""
    typefully_social_set_id: str = ""
    tavily_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5.2"
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
