from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        extra="ignore")

    MODEL_NAME: str = Field(default="qwen3:4b")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    LLM_TIMEOUT: int = Field(default=30)
    MAX_PARALLEL_REQUESTS: int = Field(default=1)

    MAX_RECURSION_LIMIT: int = Field(default=5)


settings = Settings()
