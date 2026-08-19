from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://todo:todo@localhost:5432/todo"
    database_url_test: str = "postgresql+asyncpg://todo:todo@localhost:5432/todo_test"

    session_secret: str = "change-me-to-a-random-secret"
    frontend_url: str = "http://localhost:5173"

    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    enable_test_auth: bool = False
    enable_dev_endpoints: bool = True

    ws_check_interval_default: int = 30
    ws_check_interval_min: int = 10
    ws_check_interval_max: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
