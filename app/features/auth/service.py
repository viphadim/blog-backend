from app.features.users import crud as user_crud
from app.features.roles import crud as role_crud
from app.core.security import hash_password, verify_password, create_access_token,create_refresh_token,decode_token,create_password_reset_token,create_email_verification_token
from app.core.dependencies import get_current_user_from_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.utilities.exceptions import ConflictException,UnauthorizedException,BadRequestException,NotFoundException
from app.features.users.schemas import UserResponse
from app.features.users.models import User
from app.features.users.crud import get_user_by_email,get_user_by_id,create_user
from app.features.roles.crud import get_user_permissions,get_role_by_name,assign_role_to_user
from app.core.email import send_verification_email, send_password_reset_email
from app.features.oauth.models import OAuthAccount
from app.core.config import settings
from app.core.scopes import ROLE_SCOPES

async def register_user1(db: AsyncSession, first_name: str, last_name: str, email: str, password: str) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise ConflictException("Email already registered")

    # create user
    user = await create_user(db, {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "password": hash_password(password),
        "is_active": False,
        "is_approved": False,
        "is_mail_sent": False,
        "is_deleted": False,
    })

    # assign reader role after user is in DB
    reader_role = await get_role_by_name(db, "reader")
    if reader_role:
        await assign_role_to_user(db, user.id, reader_role.id)

    # reload user with roles
    return await get_user_by_id(db, user.id)
# ─── Register ────────────────────────────────────────────────────────────
async def register_user(db: AsyncSession, first_name: str, last_name: str, email: str, password: str) -> User:
    existing = await user_crud.get_user_by_email(db, email)
    if existing:
        raise ConflictException("Email already registered")

    user = await user_crud.create_user(db, {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "password": hash_password(password),
        "is_active": False,
        "is_approved": False,
        "is_mail_sent": False,
        "is_deleted": False,
    })

    # Assign reader role
    reader_role = await role_crud.get_role_by_name(db, "reader")
    if reader_role:
        await role_crud.assign_role_to_user(db, user.id, reader_role.id)

    #  Send verification email
    token = create_email_verification_token(email)
    await send_verification_email(email, token)

    #  Mark mail as sent
    await user_crud.update_user(db, user, {"is_mail_sent": True})

    return await user_crud.get_user_by_id(db, user.id)


# ─── Email Verification ──────────────────────────────────────────────────
async def verify_email(db: AsyncSession, token: str) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "email_verification":
        raise BadRequestException("Invalid or expired verification token")

    email = payload.get("sub")
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found")

    if user.is_active:
        raise BadRequestException("Email already verified")

    return await user_crud.update_user(db, user, {"is_active": True})


# ─── Resend Verification ─────────────────────────────────────────────────
async def resend_verification_email(db: AsyncSession, email: str) -> None:
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found")

    if user.is_active:
        raise BadRequestException("Email already verified")

    token = create_email_verification_token(email)
    await send_verification_email(email, token)
    await user_crud.update_user(db, user, {"is_mail_sent": True})


async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict:
    user = await user_crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid credentials")

    if not user.is_active:
        raise UnauthorizedException("Please verify your email before logging in")

    role_names = [ur.role.name for ur in user.user_roles]

    #  Collect all scopes from all roles
    all_scopes = set()
    for role_name in role_names:
        role_scopes = ROLE_SCOPES.get(role_name, [])
        all_scopes.update(role_scopes)

    print("ROLES:", role_names)          #  debug
    print("SCOPES:", list(all_scopes))   #  debug

    access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        scopes=[s.value for s in all_scopes],  #  convert Enum to string
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

# ─── Login ───────────────────────────────────────────────────────────────
async def authenticate_user1(db: AsyncSession, email: str, password: str) -> dict:
    user = await user_crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid credentials")

    #  Check email verified
    if not user.is_active:
        raise UnauthorizedException("Please verify your email before logging in")

    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await role_crud.get_user_permissions(db, user.id)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        permissions=permissions,
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        # "token_type": "bearer",
        # "user": UserResponse.model_validate(user),
    }


async def refresh_user_token(db: AsyncSession, refresh_token: str) -> dict:
    # validate refresh token and get user
    user = await get_current_user_from_refresh_token(refresh_token, db)

    # get fresh roles and permissions from DB
    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await get_user_permissions(db, user.id)

    # embed roles and permissions in new token
    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        permissions=permissions,
    )
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        # "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

# ─── Password Reset ──────────────────────────────────────────────────────
async def forgot_password(db: AsyncSession, email: str) -> None:
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        # Don't reveal if email exists
        return

    token = create_password_reset_token(email)
    await send_password_reset_email(email, token)

async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    payload = decode_token(token)
    if not payload or payload.get("type") != "password_reset":
        raise BadRequestException("Invalid or expired reset token")

    email = payload.get("sub")
    user = await user_crud.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found")

    await user_crud.update_user(db, user, {"password": hash_password(new_password)})


async def google_oauth_callback(db: AsyncSession, code: str) -> dict:
    import httpx

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_response.json()
        if "error" in token_data:
            raise BadRequestException(f"Google OAuth error: {token_data['error_description']}")

        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_info = user_info_response.json()

    google_id = user_info.get("id")
    email = user_info.get("email")
    first_name = user_info.get("given_name", "")
    last_name = user_info.get("family_name", "")
    image_url = user_info.get("picture", None)

    #  Check if OAuth account exists
    result = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == "google",
            OAuthAccount.provider_id == google_id,
        )
    )
    oauth_account = result.scalar_one_or_none()

    if oauth_account:
        #  Existing OAuth user — just login
        user = await user_crud.get_user_by_id(db, oauth_account.user_id)
    else:
        #  Check if email already exists
        user = await user_crud.get_user_by_email(db, email)

        if not user:
            #  Create new user
            user = await user_crud.create_user(db, {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "image_url": image_url,
                "password": None,
                "is_active": True,
                "is_approved": True,
                "is_mail_sent": True,
                "is_deleted": False,
            })

            #  Assign reader role
            reader_role = await role_crud.get_role_by_name(db, "reader")
            if reader_role:
                await role_crud.assign_role_to_user(db, user.id, reader_role.id)

        #  Link OAuth account — runs for both new and existing users
        db.add(OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_id=google_id,
            access_token=token_data.get("access_token"),
        ))
        await db.commit()

        #  Reload user with roles
        user = await user_crud.get_user_by_id(db, user.id)

    #  Always reached — build and return tokens
    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await role_crud.get_user_permissions(db, user.id)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        permissions=permissions,
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

async def authenticate_user1(db: AsyncSession, email: str, password: str) -> dict:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid credentials")

    role_names = [ur.role.name for ur in user.user_roles]
    permissions = await get_user_permissions(db, user.id)

    # pass roles and permissions separately
    access_token = create_access_token(
        data={"sub": str(user.id)},
        roles=role_names,
        permissions=permissions,
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        # "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }