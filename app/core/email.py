from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

fast_mail = FastMail(conf)


async def send_verification_email(email: str, token: str) -> None:
    verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"""
        <h2>Email Verification</h2>
        <p>Click the link below to verify your email:</p>
        <a href="{verification_url}">Verify Email</a>
        <p>This link expires in 24 hours.</p>
        <p>If you did not register, ignore this email.</p>
        """,
        subtype=MessageType.html,
    )
    await fast_mail.send_message(message)


async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    message = MessageSchema(
        subject="Reset your password",
        recipients=[email],
        body=f"""
        <h2>Password Reset</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_url}">Reset Password</a>
        <p>This link expires in 1 hour.</p>
        <p>If you did not request this, ignore this email.</p>
        """,
        subtype=MessageType.html,
    )
    await fast_mail.send_message(message)