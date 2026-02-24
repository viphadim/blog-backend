from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Boolean, UniqueConstraint
from uuid import UUID, uuid4
from datetime import datetime
from app.db.session import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail: Mapped[str] = mapped_column(String(255), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="posts")
    category: Mapped["Category"] = relationship("Category", back_populates="posts")
    tags: Mapped[list["PostTag"]] = relationship("PostTag", back_populates="post")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post")
    bookmarks: Mapped[list["Bookmark"]] = relationship("Bookmark", back_populates="post")


class PostTag(Base):
    __tablename__ = "post_tags"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    tag_id: Mapped[UUID] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),)

    # Relationships
    post: Mapped["Post"] = relationship("Post", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="posts")