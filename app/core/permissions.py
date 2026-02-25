from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.features.roles.models import Permission, RolePermission, UserRole
from app.features.users.models import User
from app.core.dependencies import get_current_user


def has_permission(permission: str):
    """Dynamic permission checker — use as Depends()"""
    async def checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        #  Get all permissions for this user across all roles
        result = await db.execute(
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == current_user.id)
            .distinct()
        )
        user_permissions = list(result.scalars().all())

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: '{permission}'",
            )
        return current_user
    return checker


#  Ready-to-use permission guards
can_create_post = has_permission("post:create")
can_edit_own_post = has_permission("post:edit_own")
can_edit_any_post = has_permission("post:edit_any")
can_publish_post = has_permission("post:publish")
can_delete_any_post = has_permission("post:delete_any")
can_delete_any_comment = has_permission("comment:delete_any")
can_ban_user = has_permission("user:ban")
can_access_dashboard = has_permission("admin:dashboard")