# from app.features.users import crud as user_crud
# from app.features.roles import crud as role_crud
from app.core.security import hash_password, verify_password, create_access_token,create_refresh_token
from app.core.dependencies import get_current_user_from_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.utilities.exceptions import ConflictException,UnauthorizedException
from app.features.users.schemas import UserResponse
from app.features.users.models import User
from app.features.users.crud import get_user_by_email,get_user_by_id,create_user
from app.features.roles.crud import get_user_permissions,get_role_by_name,assign_role_to_user


async def register_user(db: AsyncSession, first_name: str, last_name: str, email: str, password: str) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise ConflictException("Email already registered")

    # create user
    user = await create_user(db, {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "password": hash_password(password),
        "is_active": False,
        "is_approved": False,
        "is_mail_sent": False,
        "is_deleted": False,
    })

    # assign reader role after user is in DB
    reader_role = await get_role_by_name(db, "reader")
    if reader_role:
        await assign_role_to_user(db, user.id, reader_role.id)

    # reload user with roles
    return await get_user_by_id(db, user.id)


async def authenticate_user1(db: AsyncSession, email: str, password: str) -> dict:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid credentials")

    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await get_user_permissions(db, user.id)

    token_data = {
        "sub": str(user.id),
        "roles": role_names,
        "permissions": permissions,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

async def refresh_user_token(db: AsyncSession, refresh_token: str) -> dict:
    # validate refresh token and get user
    user = await get_current_user_from_refresh_token(refresh_token, db)

    # get fresh roles and permissions from DB
    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await get_user_permissions(db, user.id)

    # embed roles and permissions in new token
    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        permissions=permissions,
    )
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        # "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }
async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid credentials")

    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await get_user_permissions(db, user.id)

    # pass roles and permissions separately
    access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        permissions=permissions,
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        # "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }