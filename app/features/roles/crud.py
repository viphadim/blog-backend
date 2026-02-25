from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.features.roles.models import Role, Permission, RolePermission, UserRole
from app.features.users.models import User

async def get_user_with_roles(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_roles).selectinload(UserRole.role)
        )
    )
    user = result.scalar_one()
    return user
# ─── Role ────────────────────────────────────────────────
async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def get_all_roles(db: AsyncSession) -> list[Role]:
    result = await db.execute(select(Role))
    return result.scalars().all()


# ─── Permission ───────────────────────────────────────────
async def get_permission_by_name(db: AsyncSession, name: str) -> Permission | None:
    result = await db.execute(select(Permission).where(Permission.name == name))
    return result.scalar_one_or_none()


async def get_all_permissions(db: AsyncSession) -> list[Permission]:
    result = await db.execute(select(Permission))
    return result.scalars().all()


# ─── UserRole ─────────────────────────────────────────────
async def get_user_roles(db: AsyncSession, user_id: UUID) -> list[UserRole]:
    result = await db.execute(
        select(UserRole)
        .where(UserRole.user_id == user_id)
        .options(joinedload(UserRole.role))
    )
    return result.scalars().all()


# async def assign_role_to_user(db: AsyncSession, user_id: UUID, role_id: UUID) -> UserRole:
#     user_role = UserRole(user_id=user_id, role_id=role_id)
#     db.add(user_role)
#     await db.commit()
#     await db.refresh(user_role)
#     return user_role

async def assign_role_to_user(db: AsyncSession, user_id: UUID, role_id: UUID) -> UserRole:
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    await db.commit()
    #  Don't use db.refresh — reload with joinedload instead
    result = await db.execute(
        select(UserRole)
        .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        .options(joinedload(UserRole.role))
    )
    return result.unique().scalar_one()

async def remove_role_from_user(db: AsyncSession, user_id: UUID, role_id: UUID) -> None:
    result = await db.execute(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
    )
    user_role = result.scalar_one_or_none()
    if user_role:
        await db.delete(user_role)
        await db.commit()


# ─── User Permissions ─────────────────────────────────────
async def get_user_permissions(db: AsyncSession, user_id: UUID) -> list[str]:
    """Get all permissions for a user across all their roles"""
    result = await db.execute(
        select(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
        .distinct()
    )
    return list(result.scalars().all())