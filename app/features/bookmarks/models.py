from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from uuid import UUID, uuid4
from datetime import datetime
from app.db.session import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_user_post_bookmark"),)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")
    post: Mapped["Post"] = relationship("Post", back_populates="bookmarks")