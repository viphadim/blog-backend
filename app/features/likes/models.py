from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from uuid import UUID, uuid4
from datetime import datetime
from app.db.session import Base


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    comment_id: Mapped[UUID] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)  # like comment too
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_user_post_like"),
        UniqueConstraint("user_id", "comment_id", name="uq_user_comment_like"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="likes")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="likes")