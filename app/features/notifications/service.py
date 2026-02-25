from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.notifications import crud
from app.features.notifications.models import NotificationType
from app.features.users.models import User
from app.utilities.exceptions import NotFoundException


async def get_my_notifications(db: AsyncSession, user: User):
    return await crud.get_user_notifications(db, user.id)


async def get_unread_count(db: AsyncSession, user: User):
    return await crud.get_unread_count(db, user.id)


async def mark_as_read(db: AsyncSession, user: User, notification_id: UUID) -> None:
    await crud.mark_as_read(db, notification_id, user.id)


async def mark_all_as_read(db: AsyncSession, user: User) -> None:
    await crud.mark_all_as_read(db, user.id)


async def delete_notification(db: AsyncSession, user: User, notification_id: UUID) -> None:
    await crud.delete_notification(db, notification_id, user.id)


# ─── Notification Triggers ────────────────────────────────────────────────
async def notify_post_liked(db: AsyncSession, actor_id: UUID, post) -> None:
    await crud.create_notification(
        db,
        receiver_id=post.user_id,  # notify post owner
        actor_id=actor_id,
        type=NotificationType.POST_LIKED,
        post_id=post.id,
    )


async def notify_post_commented(db: AsyncSession, actor_id: UUID, post) -> None:
    await crud.create_notification(
        db,
        receiver_id=post.user_id,  # notify post owner
        actor_id=actor_id,
        type=NotificationType.POST_COMMENTED,
        post_id=post.id,
    )


async def notify_comment_replied(db: AsyncSession, actor_id: UUID, parent_comment) -> None:
    await crud.create_notification(
        db,
        receiver_id=parent_comment.user_id,  # notify comment owner
        actor_id=actor_id,
        type=NotificationType.COMMENT_REPLIED,
        comment_id=parent_comment.id,
    )


async def notify_comment_liked(db: AsyncSession, actor_id: UUID, comment) -> None:
    await crud.create_notification(
        db,
        receiver_id=comment.user_id,  # notify comment owner
        actor_id=actor_id,
        type=NotificationType.COMMENT_LIKED,
        comment_id=comment.id,
    )


async def notify_post_bookmarked(db: AsyncSession, actor_id: UUID, post) -> None:
    await crud.create_notification(
        db,
        receiver_id=post.user_id,  # notify post owner
        actor_id=actor_id,
        type=NotificationType.POST_BOOKMARKED,
        post_id=post.id,
    )