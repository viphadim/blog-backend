from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.session import get_db
from app.features.auth.shcemas import (
    RegisterRequest, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    ResendVerificationRequest, MessageResponse,
)
from app.features.auth.service import register_user, authenticate_user, refresh_user_token
from app.features.users.schemas import UserResponse
from app.utilities.baseResponse import BaseResponse
from app.features.auth.service import (
    register_user, authenticate_user, refresh_user_token,
    verify_email, resend_verification_email,
    forgot_password, reset_password, google_oauth_callback,
)
from app.core.config import settings
from fastapi.responses import RedirectResponse
from typing import Optional

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



# ─── Email Verification ──────────────────────────────────────────────────
@router.get("/verify-email", response_model=BaseResponse[UserResponse])
async def verify_email_route(token: str, db: AsyncSession = Depends(get_db)):
    user = await verify_email(db, token)
    return BaseResponse(
        success=True, status_code=200, message="Email verified successfully",
        timestamp=datetime.now(), data=UserResponse.model_validate(user),
    )


@router.post("/resend-verification", response_model=BaseResponse[MessageResponse])
async def resend_verification(body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    await resend_verification_email(db, body.email)
    return BaseResponse(
        success=True, status_code=200,
        message="Verification email sent successfully",
        timestamp=datetime.now(),
        data=MessageResponse(message="Please check your email"),
    )


# ─── Password Reset ──────────────────────────────────────────────────────
@router.post("/forgot-password", response_model=BaseResponse[MessageResponse])
async def forgot_password_route(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await forgot_password(db, body.email)
    return BaseResponse(
        success=True, status_code=200,
        message="If this email exists, a reset link has been sent",
        timestamp=datetime.now(),
        data=MessageResponse(message="Please check your email"),
    )


@router.post("/reset-password", response_model=BaseResponse[MessageResponse])
async def reset_password_route(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await reset_password(db, body.token, body.new_password)
    return BaseResponse(
        success=True, status_code=200, message="Password reset successfully",
        timestamp=datetime.now(),
        data=MessageResponse(message="You can now login with your new password"),
    )


# ─── Google OAuth ────────────────────────────────────────────────────────
@router.get("/auth/google/login")
async def google_login():
    print("REDIRECT URI:", settings.GOOGLE_REDIRECT_URI)  #  debug
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
    )
    return RedirectResponse(url=google_auth_url)

@router.get("/auth/google/callback", response_model=BaseResponse[TokenResponse])
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
    iss: Optional[str] = None,
    scope: Optional[str] = None,
    authuser: Optional[str] = None,
    prompt: Optional[str] = None,
):
    tokens = await google_oauth_callback(db, code)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Google login successful",
        timestamp=datetime.now(),
        data=TokenResponse(**tokens),
    )

# @router.get("/auth/google/callback", response_model=BaseResponse[TokenResponse])
# async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
#     tokens = await google_oauth_callback(db, code)
#     return BaseResponse(
#         success=True, status_code=200, message="Google login successful",
#         timestamp=datetime.now(), data=TokenResponse(**tokens),
#     )


# @router.post("/logout")
# async def logout():
#     return BaseResponse(
#         success=True, status_code=200,
#         message="Successfully logged out. Please delete your tokens.",
#         timestamp=datetime.now(), data=None,
#     )