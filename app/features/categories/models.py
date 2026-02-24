from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text
from uuid import UUID, uuid4
from datetime import datetime
from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")