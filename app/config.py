from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "YT Automation"
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    DEBUG: bool = True
    BASE_URL: str = "http://localhost:8004"
    PORT: int = 8004

    DATABASE_URL: str = "sqlite:///./youtube_automation.db"

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_BASE_URL: str = "https://api.elevenlabs.io/v1"

    YOUTUBE_DATA_API_KEY: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""

    UPLOAD_DIR: str = "app/uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
