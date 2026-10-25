from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timezone
from fastapi import HTTPException, status, Depends, Header
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, jwk
from sqlalchemy.orm import Session
from time import mktime, gmtime
from uuid import UUID
import asyncio
import json
import secrets

from auth import models, schemas
from auth.schemas import Token, TokenType
from db import get_db, redis_conn, JWKS_PUB_KEY, JWKS_EXP_KEY, JWKS_PRIV_KEY
from settings import settings


def get_webhook_user(user_id: UUID, token: str = "", db: Session = Depends(get_db)) -> schemas.User:
    """
    Resolves the user for a provider webhook. The webhook URL carries the user's secret token, so a caller who only
    knows (or guesses) a user id can't inject messages. Unknown user and bad token look the same to the caller.
    """
    user = db.query(models.User).get(user_id)
    if not user or not secrets.compare_digest(token, user.webhook_token):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return schemas.User.from_orm(user)


async def decode_token(token: str) -> Token:
    keys = await load_keys()
    decoded = Token(**jwt.decode(token, keys))
    if decoded.exp > datetime.now(timezone.utc):
        return decoded
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User not logged in or token expired."
    )


async def create_token(username: str, token_type: TokenType = TokenType.ACCESS) -> str:
    # Ensures a signing key exists (and rotates it if expired) before we read it
    await load_keys()
    redis = await redis_conn()
    key = await redis.get(JWKS_PRIV_KEY)

    token = Token(
        sub=username,
        type=token_type
    )
    if token_type == TokenType.REFRESH:
        token.exp = datetime.utcnow() + settings().REFRESH_TOKEN_LIFETIME
    return jwt.encode(token.dict(), key, algorithm='RS256')


async def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> schemas.User:
    scheme, param = get_authorization_scheme_param(authorization)
    decoded = await decode_token(param)
    if decoded.type == TokenType.ACCESS:
        user = db.query(models.User).filter(models.User.username == decoded.sub).first()
        return schemas.User.from_orm(user)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User not logged in or token expired."
    )


async def load_keys():
    redis = await redis_conn()

    keys, expiry = await asyncio.gather(redis.get(JWKS_PUB_KEY), redis.get(JWKS_EXP_KEY))

    if keys:
        keys = json.loads(keys)
    if expiry:
        expiry = int(expiry)

    current_time = int(mktime(gmtime()))
    if not expiry or expiry < current_time:
        exp = redis.set(JWKS_EXP_KEY, current_time + 86400)

        if not keys:
            keys = {'keys': []}
        if 'keys' not in keys:
            keys['keys'] = []

        priv_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pubkey = jwk.construct(priv_key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                                  format=serialization.PublicFormat.PKCS1),
                               algorithm='RS256')
        keys['keys'].append(pubkey.to_dict())
        if len(keys['keys']) > 2:
            keys['keys'].pop(0)

        await asyncio.gather(
            redis.set(JWKS_PUB_KEY, json.dumps(keys)),
            redis.set(JWKS_PRIV_KEY, priv_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                            format=serialization.PrivateFormat.PKCS8,
                                                            encryption_algorithm=serialization.NoEncryption())),
            exp
        )

    return keys
