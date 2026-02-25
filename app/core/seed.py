from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.roles.models import Role, Permission, RolePermission
from app.features.roles.permissions import ROLE_PERMISSIONS


async def seed_roles_and_permissions(db: AsyncSession) -> None:

    # ─── Step 1: Seed Permissions ─────────────────────────────
    all_permissions = set(p for perms in ROLE_PERMISSIONS.values() for p in perms)

    for perm_name in all_permissions:
        existing = await db.execute(select(Permission).where(Permission.name == perm_name))
        if not existing.scalar_one_or_none():
            db.add(Permission(name=perm_name, description=perm_name.replace(":", " ").title()))

    await db.commit()
    print("✅ Permissions seeded")

    # ─── Step 2: Seed Roles ───────────────────────────────────
    for role_name in ROLE_PERMISSIONS:
        existing = await db.execute(select(Role).where(Role.name == role_name))
        if not existing.scalar_one_or_none():
            db.add(Role(name=role_name, description=f"Default {role_name} role"))

    await db.commit()
    print("✅ Roles seeded")

    # ─── Step 3: Seed Role Permissions ────────────────────────
    for role_name, permissions in ROLE_PERMISSIONS.items():
        role_result = await db.execute(select(Role).where(Role.name == role_name))
        role = role_result.scalar_one_or_none()

        for perm_name in permissions:
            perm_result = await db.execute(select(Permission).where(Permission.name == perm_name))
            perm = perm_result.scalar_one_or_none()

            existing = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            )
            if not existing.scalar_one_or_none():
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))

    await db.commit()
    print("✅ Role permissions seeded")
    print("✅ Seeding complete!")


async def seed_admin_user(db: AsyncSession, email: str, password: str) -> None:
    """Create first admin user"""
    from app.features.users.models import User
    from app.features.roles.models import UserRole
    from app.core.security import hash_password

    # Check if admin already exists
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        print("✅ Admin user already exists")
        return

    # Create admin user
    admin = User(
        email=email,
        password=hash_password(password),
        first_name="Admin",
        last_name="User",
        full_name="Admin User",
        is_active=True,      # ✅ admin is active by default
        is_approved=True,
        is_mail_sent=True,
        is_deleted=False,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    # Assign admin role
    admin_role = await db.execute(select(Role).where(Role.name == "admin"))
    role = admin_role.scalar_one_or_none()
    if role:
        db.add(UserRole(user_id=admin.id, role_id=role.id))
        await db.commit()

    print(f"✅ Admin user created: {email}")