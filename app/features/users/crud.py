from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.features.users.models import User
from app.features.roles.models import UserRole


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    return result.unique().scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role) 
        )
    )
    return result.unique().scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.email == email)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    return result.unique().scalar_one_or_none()


async def create_user(db: AsyncSession, data: dict) -> User:
    user = User(**data)
    db.add(user)
    await db.commit()

    # Reload with roles after commit
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    return result.unique().scalar_one()


async def update_user(db: AsyncSession, user: User, data: dict) -> User:
    for key, value in data.items():
        setattr(user, key, value)
    await db.commit()

    # Reload with roles after commit
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
    )
    return result.unique().scalar_one()


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()