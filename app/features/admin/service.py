from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.admin import crud
from app.features.users import crud as user_crud
from app.features.roles import crud as role_crud
from app.features.admin.schemas import DashboardStatsResponse
from app.utilities.exceptions import NotFoundException, ConflictException


async def get_dashboard_stats(db: AsyncSession) -> DashboardStatsResponse:
    stats = await crud.get_dashboard_stats(db)
    return DashboardStatsResponse(**stats)


async def ban_user(db: AsyncSession, user_id: UUID) -> None:
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    await user_crud.update_user(db, user, {"is_active": False, "is_deleted": True})


async def unban_user(db: AsyncSession, user_id: UUID) -> None:
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    await user_crud.update_user(db, user, {"is_active": True, "is_deleted": False})


async def assign_role(db: AsyncSession, user_id: UUID, role_name: str) -> None:
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    role = await role_crud.get_role_by_name(db, role_name)
    if not role:
        raise NotFoundException(f"Role '{role_name}' not found")

    # ✅ Check if user already has this role
    user_role_names = [ur.role.name for ur in user.user_roles]
    if role_name in user_role_names:
        raise ConflictException(f"User already has role '{role_name}'")

    await role_crud.assign_role_to_user(db, user_id, role.id)


async def revoke_role(db: AsyncSession, user_id: UUID, role_name: str) -> None:
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    role = await role_crud.get_role_by_name(db, role_name)
    if not role:
        raise NotFoundException(f"Role '{role_name}' not found")

    await role_crud.remove_role_from_user(db, user_id, role.id)