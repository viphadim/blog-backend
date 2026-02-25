from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.session import get_db
from app.features.auth.shcemas import RegisterRequest, TokenResponse, RefreshTokenRequest
from app.features.auth.service import register_user, authenticate_user, refresh_user_token
from app.features.users.schemas import UserResponse
from app.utilities.baseResponse import BaseResponse

router = APIRouter(prefix="", tags=["Auth"])


@router.post("/register", response_model=BaseResponse[UserResponse])
async def register(user: RegisterRequest, db: AsyncSession = Depends(get_db)):
    new_user = await register_user(
        db,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
    )
    return BaseResponse(
        success=True,
        status_code=201,
        message="User created successfully",
        timestamp=datetime.now(),
        data=UserResponse.model_validate(new_user),  
    )


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, email=form_data.username, password=form_data.password)


@router.post("/login", response_model=BaseResponse[TokenResponse])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    tokens = await authenticate_user(db, email=form_data.username, password=form_data.password)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Login successfully",
        timestamp=datetime.now(),
        data=TokenResponse(**tokens),
    )


@router.post("/refresh", response_model=BaseResponse[TokenResponse])
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    tokens = await refresh_user_token(db, body.refresh_token) 
    return BaseResponse(
        success=True,
        status_code=200,
        message="Token refreshed successfully",
        timestamp=datetime.now(),
        data=TokenResponse(**tokens),
    )