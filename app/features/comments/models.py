from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from uuid import UUID, uuid4
from datetime import datetime
from app.db.session import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[UUID] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)  # reply to comment
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    replies: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent")
    parent: Mapped["Comment"] = relationship("Comment", back_populates="replies", remote_side="Comment.id")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="comment")