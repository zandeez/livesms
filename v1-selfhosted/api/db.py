import aioredis
from aioredis import Redis
from async_lru import alru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

JWKS_PUB_KEY = 'jwks'
JWKS_PRIV_KEY = 'jwks_private'
JWKS_EXP_KEY = 'jwks_expiry'

engine = create_engine(settings().DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@alru_cache()
async def redis_conn() -> Redis:
    return await aioredis.create_redis_pool(settings().REDIS_URL, db=settings().REDIS_DB)
