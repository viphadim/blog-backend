from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.roles import crud
from app.features.users import crud as user_crud
from app.utilities.exceptions import NotFoundException, ConflictException
from app.features.roles.models import Role


async def get_all_roles(db: AsyncSession) -> list[Role]:
    return await crud.get_all_roles(db)


async def get_role_by_id(db: AsyncSession, role_id: UUID) -> Role:
    role = await crud.get_role_by_id(db, role_id)
    if not role:
        raise NotFoundException("Role not found")
    return role

async def assign_role(db: AsyncSession, user_id: UUID, role_name: str):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    role = await crud.get_role_by_name(db, role_name)
    if not role:
        raise NotFoundException(f"Role '{role_name}' not found")

    # Check if user already has this role
    user_roles = await crud.get_user_roles(db, user_id)
    existing_role_ids = [ur.role_id for ur in user_roles]
    if role.id in existing_role_ids:
        raise ConflictException(f"User already has role '{role_name}'")

    return await crud.assign_role_to_user(db, user_id, role.id)


async def remove_role(db: AsyncSession, user_id: UUID, role_name: str):
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    role = await crud.get_role_by_name(db, role_name)
    if not role:
        raise NotFoundException(f"Role '{role_name}' not found")

    await crud.remove_role_from_user(db, user_id, role.id)


async def get_user_permissions(db: AsyncSession, user_id: UUID) -> list[str]:
    return await crud.get_user_permissions(db, user_id)