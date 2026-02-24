import uuid
from sqlalchemy import Column, String, Boolean, DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email            = Column(String(255), unique=True, index=True, nullable=False)
    first_name         = Column(String(50),  index=True, nullable=False)
    last_name         = Column(String(50), index=True, nullable=False)
    full_name         = Column(String(50),  index=True, nullable=False)
    # hashed_password  = Column(String, nullable=True)   # nullable for OAuth-only accounts
    # is_admin         = Column(Boolean, default=False, nullable=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)  # Added from new code
    is_mail_sent = Column(Boolean, default=False)
    is_deleted= Column(Boolean, default=False)
    password = Column(String)
    image_url = Column(String, nullable=True)
    position = Column(String, nullable=True)  # Added from new code
    phone_number = Column(String, nullable=True)  # Added from new code
    # oauth_accounts   = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)

    # relationships (optional but recommended)
    # user = relationship("User", back_populates="roles")
    # role = relationship("Role", back_populates="users")


