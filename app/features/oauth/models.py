from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint
from uuid import UUID, uuid4
from datetime import datetime
from app.db.session import Base


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)   # google, github, facebook
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)  # provider's user id
    access_token: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (UniqueConstraint("provider", "provider_id", name="uq_provider_account"),)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")