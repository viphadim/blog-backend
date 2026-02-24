from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.features.users.models import User
from app.core.security import hash_password, verify_password, create_access_token,create_refresh_token


async def register_user(db: AsyncSession, first_name: str, last_name: str,email: str, password: str):
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
        password=hash_password(password),
        full_name=f"{first_name} {last_name}",
        phone_number=None,
        is_active=False,
        is_approved=False,
        is_mail_sent=False,
        is_deleted=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})  # no scopes in refresh token

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        # "token_type": "bearer"
        
    }

