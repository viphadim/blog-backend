from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.features.users.models import User
from app.core.security import hash_password, verify_password
from typing import List
from typing import Optional


from sqlalchemy import select
from fastapi import HTTPException, status

async def create_user(
    db: AsyncSession,
    first_name: str,
    last_name: str,
    email: str,
    phone_number: Optional[str] = None
):
    #  check if email already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # create new user
    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        full_name=f"{first_name} {last_name}",
        phone_number=phone_number,
        is_active=False,
        is_approved=False,
        is_mail_sent=False,
        is_deleted=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user_imp(
    db: AsyncSession,
    id: str,
    first_name: str,
    last_name: str,
):
    result = await db.execute(select(User).where(User.id == id))
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # update fields
    existing_user.first_name = first_name
    existing_user.last_name = last_name
    existing_user.full_name = f"{first_name} {last_name}"

    await db.commit()
    await db.refresh(existing_user)

    return existing_user

async def delete_user_imp(db: AsyncSession, id: str):
    qurrey=await db.execute(select(User).where(User.id == id,User.is_deleted == False))
    user = qurrey.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or already deleted")
    user.is_deleted = True

    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_id(db: AsyncSession, id: str):
    result = await db.execute(select(User).where(User.id == id, User.is_deleted == False))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

async def authenticate_user(db: AsyncSession, id: str, password: str):
    user = await get_user_by_id(db, id)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def get_all_users(db:AsyncSession)->List[User]:
    qurrey=await db.execute(select(User).where(User.is_deleted == False))
    return qurrey.scalars().all()