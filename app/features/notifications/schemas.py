from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.features.notifications.models import NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    type: NotificationType
    is_read: bool
    post_id: Optional[UUID] = None
    comment_id: Optional[UUID] = None
    created_at: datetime
    actor: Optional[dict] = None  

    model_config = {"from_attributes": True}

    @classmethod
    def from_notification(cls, n) -> "NotificationResponse":
        return cls(
            id=n.id,
            type=n.type,
            is_read=n.is_read,
            post_id=n.post_id,
            comment_id=n.comment_id,
            created_at=n.created_at,
            actor={
                "id": str(n.actor.id),
                "full_name": n.actor.full_name,
                "image_url": n.actor.image_url,
            } if n.actor else None,
        )


class UnreadCountResponse(BaseModel):
    unread_count: int