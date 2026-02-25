from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from pydantic import  ValidationError
from app.db.session import get_db
from app.core.security import SECRET_KEY, ALGORITHM,decode_token
from app.features.users.models import User
from app.features.users.crud import get_user_by_id
from app.features.roles.models import UserRole
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception

        if payload.get("type") != "access":
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    #  Eager load roles
    result = await db.execute(
        select(User)
        .where(User.id == UUID(user_id))
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    user = result.unique().scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_from_refresh_token(
    token: str,
    db: AsyncSession,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception

        # Reject access tokens used as refresh tokens
        if payload.get("type") != "refresh":
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Eager load roles
    result = await db.execute(
        select(User)
        .where(User.id == UUID(user_id))
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    user = result.unique().scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user