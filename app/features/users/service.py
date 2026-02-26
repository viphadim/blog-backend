from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.users import crud
from app.features.users.models import User
from app.utilities.exceptions import NotFoundException, ConflictException
from app.features.users.schemas import UpdateProfileRequest


async def get_all_users(db: AsyncSession) -> list[User]:
    return await crud.get_all_users(db)


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    return user


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


async def update_profile(db: AsyncSession, user: User, data: UpdateProfileRequest) -> User:
    update_data = data.model_dump(exclude_unset=True)

    # ✅ Auto update full_name if first or last name changes
    first_name = update_data.get("first_name", user.first_name)
    last_name = update_data.get("last_name", user.last_name)
    if "first_name" in update_data or "last_name" in update_data:
        update_data["full_name"] = f"{first_name} {last_name}"

    return await crud.update_user(db, user, update_data)