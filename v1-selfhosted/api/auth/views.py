from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from auth import models, schemas
from auth.utils import create_token, decode_token, load_keys, get_current_user
from db import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/token", response_model=schemas.TokenResponse)
async def issue_token(login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_request.username).first()
    if user and pwd_context.verify(login_request.password, user.password):
        return schemas.TokenResponse(accessToken=await create_token(login_request.username),
                                     refreshToken=await create_token(login_request.username,
                                                                     token_type=schemas.TokenType.REFRESH))
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/token/refresh", response_model=schemas.TokenResponse, response_model_exclude_none=True)
async def refresh_token(request: schemas.TokenRequest):
    decoded = await decode_token(request.token)
    if decoded.type == schemas.TokenType.REFRESH:
        return schemas.TokenResponse(accessToken=await create_token(decoded.sub))
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid refresh token"
    )


@router.post("/token/verify", response_model=schemas.SuccessResponse)
async def verify_token(request: schemas.TokenRequest):
    await decode_token(request.token)
    return schemas.SuccessResponse()


@router.get("/user", response_model=schemas.APISettings)
async def get_user(user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    return schemas.APISettings.from_orm(db_user)


@router.post("/user")
async def update_user(api_settings: schemas.APISettings, user: schemas.User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    for k, v in api_settings.dict().items():
        if k not in ("id", "api_type", "webhook_token"):
            setattr(db_user, k, str(v))
        db_user.api_type = api_settings.api_type.value

    db.commit()


@router.post("/user/password", response_model=schemas.SuccessResponse)
async def change_password(request: schemas.ChangePasswordRequest, user: schemas.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    await set_user_password(request.oldPassword, request.newPassword, user, db)


@router.get("/jwks", response_model=schemas.JWKS)
async def get_jwks():
    return await load_keys()


async def set_user_password(old_password: str, new_password: str, user: schemas.User, db: Session):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if not pwd_context.verify(old_password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Old password incorrect"
        )

    db_user.password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(db_user)
