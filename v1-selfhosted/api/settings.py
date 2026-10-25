import os
from datetime import timedelta
from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    REDIS_URL: str = "redis://localhost"
    REDIS_DB: int = 0
    REFRESH_TOKEN_LIFETIME: timedelta = timedelta(days=1)
    ACCESS_TOKEN_LIFETIME: timedelta = timedelta(minutes=5)
    WS_TOKEN_EXPIRY: int = 10
    CORS_ORIGINS: List[str] = ['http://localhost:8080', 'http://websms.localhost']

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


@lru_cache
def settings():
    return Settings()
