import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from settings import settings


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: Optional[str]


class TokenRequest(BaseModel):
    token: str


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str


class APIType(Enum):
    SIMWOOD = 'simwood'
    SINCH = 'sinch'


class User(BaseModel):
    class Config:
        orm_mode = True

    id: UUID
    username: str
    email: Optional[str]
    is_admin: bool
    number: Optional[str]


class APISettings(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        fields = {
            'api_type': 'apiType',
            'api_account': 'apiAccount',
            'api_username': 'apiUsername',
            'api_password': 'apiPassword',
            'webhook_token': 'webhookToken',
        }

    id: UUID
    number: Optional[str]
    api_type: Optional[APIType]
    api_account: Optional[str]
    api_username: Optional[str]
    api_password: Optional[str]
    webhook_token: Optional[str]


class TokenType(str, Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class Token(BaseModel):
    sub: str
    type: TokenType = TokenType.ACCESS
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iat: datetime = Field(default_factory=datetime.utcnow)
    nbf: datetime = Field(default_factory=datetime.utcnow)
    exp: datetime = Field(default_factory=lambda: datetime.utcnow() + settings().ACCESS_TOKEN_LIFETIME)


class JWK(BaseModel):
    alg: str = "RS256"
    kty: str = "RSA"
    n: str
    e: str


class JWKS(BaseModel):
    keys: List[JWK]


class SuccessResponse(BaseModel):
    message: str = "OK"
