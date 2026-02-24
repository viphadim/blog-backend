from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.features.users import crud
from app.features.users.schemas import UserResponse
from app.features.users.models import User
from app.core.security import hash_password
from app.utilities.exceptions import NotFoundException, ConflictException

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")  
    return user

async def get_all_users(db: AsyncSession) -> list[User]:
    return await crud.get_all_users(db)

async def update_user(db: AsyncSession, user_id: UUID, data: dict) -> User:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    return await crud.update_user(db, user, data)


async def delete_user(db: AsyncSession, user_id: UUID) -> None:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    await crud.delete_user(db, user)