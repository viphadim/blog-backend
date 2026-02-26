from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Optional
from pydantic import ValidationError

from app.db.session import get_db
from app.core.security import decode_token
from app.features.users.models import User
from app.features.roles.models import UserRole
from app.core.scopes import Scope


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        Scope.ME_READ: "Read own profile",
        Scope.ME_WRITE: "Update own profile",
        Scope.POST_CREATE: "Create posts",
        Scope.POST_EDIT_OWN: "Edit own posts",
        Scope.POST_EDIT_ANY: "Edit any post",
        Scope.POST_PUBLISH: "Publish posts",
        Scope.POST_DELETE_OWN: "Delete own posts",
        Scope.POST_DELETE_ANY: "Delete any post",
        Scope.COMMENT_CREATE: "Create comments",
        Scope.COMMENT_DELETE_OWN: "Delete own comments",
        Scope.COMMENT_DELETE_ANY: "Delete any comment",
        Scope.USER_BAN: "Ban users",
        Scope.ADMIN_DASHBOARD: "Access admin dashboard",
    }
)

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


# ✅ Main dependency — follows FastAPI docs exactly
async def get_current_user(
    security_scopes: SecurityScopes,  # ✅ FastAPI auto injects required scopes
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    authenticate_value = (
        f'Bearer scope="{security_scopes.scope_str}"'
        if security_scopes.scopes
        else "Bearer"
    )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
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

        # ✅ Extract scopes from token
        token_scopes: list[str] = payload.get("scopes", [])

    except (JWTError, ValidationError):
        raise credentials_exception

    # ✅ Check every required scope exists in token
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required scope: '{scope}'",
                headers={"WWW-Authenticate": authenticate_value},
            )

    result = await db.execute(
        select(User)
        .where(User.id == UUID(user_id))
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    user = result.unique().scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


# ✅ Optional — for public endpoints that behave differently when logged in
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(
            select(User)
            .where(User.id == UUID(user_id))
            .options(joinedload(User.user_roles).joinedload(UserRole.role))
        )
        return result.unique().scalar_one_or_none()
    except Exception:
        return None


# ✅ For refresh token endpoint
async def get_current_user_from_refresh_token(token: str, db: AsyncSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None or payload.get("type") != "refresh":
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User)
        .where(User.id == UUID(user_id))
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    user = result.unique().scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import jwt, JWTError
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from uuid import UUID
# from pydantic import  ValidationError
# from app.db.session import get_db
# from app.core.security import SECRET_KEY, ALGORITHM,decode_token
# from app.features.users.models import User
# from app.features.users.crud import get_user_by_id
# from app.features.roles.models import UserRole
# from sqlalchemy.future import select
# from sqlalchemy.orm import joinedload
# from typing import Optional

# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_db),
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = decode_token(token)
#         if payload is None:
#             raise credentials_exception

#         if payload.get("type") != "access":
#             raise credentials_exception

#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception

#     except JWTError:
#         raise credentials_exception

#     #  Eager load roles
#     result = await db.execute(
#         select(User)
#         .where(User.id == UUID(user_id))
#         .options(joinedload(User.user_roles).joinedload(UserRole.role))
#     )
#     user = result.unique().scalar_one_or_none()

#     if user is None:
#         raise credentials_exception

#     return user


# async def get_current_user_from_refresh_token(
#     token: str,
#     db: AsyncSession,
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid refresh token",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = decode_token(token)
#         if payload is None:
#             raise credentials_exception

#         # Reject access tokens used as refresh tokens
#         if payload.get("type") != "refresh":
#             raise credentials_exception

#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception

#     except JWTError:
#         raise credentials_exception

#     # Eager load roles
#     result = await db.execute(
#         select(User)
#         .where(User.id == UUID(user_id))
#         .options(joinedload(User.user_roles).joinedload(UserRole.role))
#     )
#     user = result.unique().scalar_one_or_none()

#     if user is None:
#         raise credentials_exception

#     return user


# async def get_current_user_optional(
#     token: Optional[str] = Depends(oauth2_scheme_optional),
#     db: AsyncSession = Depends(get_db),
# ) -> User | None:
#     if not token:
#         return None
#     try:
#         payload = decode_token(token)
#         if not payload or payload.get("type") != "access":
#             return None
#         user_id = payload.get("sub")
#         if not user_id:
#             return None
#         result = await db.execute(
#             select(User)
#             .where(User.id == UUID(user_id))
#             .options(joinedload(User.user_roles).joinedload(UserRole.role))
#         )
#         return result.unique().scalar_one_or_none()
#     except Exception:
#         return None
