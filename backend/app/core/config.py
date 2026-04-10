from functools import lru_cache
import os
from pathlib import Path

from pydantic import BaseModel


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Fintech Test")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    api_v1_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bravo")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "my_secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    webhook_target_url: str = os.getenv("WEBHOOK_TARGET_URL", "http://localhost:8000/api/v1/webhooks/mock-receiver")
    webhook_timeout_seconds: float = float(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "5.0"))
    worker_poll_seconds: float = float(os.getenv("WORKER_POLL_SECONDS", "1.0"))
    sse_poll_seconds: float = float(os.getenv("SSE_POLL_SECONDS", "1.0"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
