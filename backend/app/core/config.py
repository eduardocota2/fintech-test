from functools import lru_cache

from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Validador de Crédito Fintech"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bravo"
    jwt_secret_key: str = "my_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

@lru_cache()
def get_settings() -> Settings:
    return Settings()