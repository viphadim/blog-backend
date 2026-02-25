from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from uuid import UUID

from app.features.notifications.models import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    receiver_id: UUID,
    actor_id: UUID,
    type: NotificationType,
    post_id: UUID = None,
    comment_id: UUID = None,
) -> None:
    # Don't notify yourself
    if receiver_id == actor_id:
        return

    notification = Notification(
        receiver_id=receiver_id,
        actor_id=actor_id,
        type=type,
        post_id=post_id,
        comment_id=comment_id,
    )
    db.add(notification)
    await db.commit()


async def get_user_notifications(db: AsyncSession, user_id: UUID) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.receiver_id == user_id)
        .options(joinedload(Notification.actor))
        .order_by(Notification.created_at.desc())
    )
    return result.unique().scalars().all()


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        select(func.count())
        .where(Notification.receiver_id == user_id, Notification.is_read == False)
    )
    return result.scalar()


async def mark_as_read(db: AsyncSession, notification_id: UUID, user_id: UUID) -> None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.receiver_id == user_id,
        )
    )
    notification = result.scalar_one_or_none()
    if notification:
        notification.is_read = True
        await db.commit()


async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> None:
    result = await db.execute(
        select(Notification).where(
            Notification.receiver_id == user_id,
            Notification.is_read == False,
        )
    )
    notifications = result.scalars().all()
    for n in notifications:
        n.is_read = True
    await db.commit()


async def delete_notification(db: AsyncSession, notification_id: UUID, user_id: UUID) -> None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.receiver_id == user_id,
        )
    )
    notification = result.scalar_one_or_none()
    if notification:
        await db.delete(notification)
        await db.commit()