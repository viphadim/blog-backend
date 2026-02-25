from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Enum
from uuid import UUID, uuid4
from datetime import datetime
import enum
from app.db.session import Base


class NotificationType(str, enum.Enum):
    POST_LIKED = "post_liked"
    POST_COMMENTED = "post_commented"
    COMMENT_REPLIED = "comment_replied"
    COMMENT_LIKED = "comment_liked"
    POST_BOOKMARKED = "post_bookmarked"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # Who receives the notification
    receiver_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Who triggered the notification
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    # Reference to what was liked/commented etc.
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    comment_id: Mapped[UUID] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id])
    actor: Mapped["User"] = relationship("User", foreign_keys=[actor_id])