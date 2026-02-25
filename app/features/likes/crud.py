from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from uuid import UUID

from app.features.likes.models import Like


async def get_post_like(db: AsyncSession, user_id: UUID, post_id: UUID) -> Like | None:
    result = await db.execute(
        select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
    )
    return result.scalar_one_or_none()


async def get_comment_like(db: AsyncSession, user_id: UUID, comment_id: UUID) -> Like | None:
    result = await db.execute(
        select(Like).where(Like.user_id == user_id, Like.comment_id == comment_id)
    )
    return result.scalar_one_or_none()


async def get_post_likes_count(db: AsyncSession, post_id: UUID) -> int:
    result = await db.execute(
        select(func.count()).where(Like.post_id == post_id)
    )
    return result.scalar()


async def get_comment_likes_count(db: AsyncSession, comment_id: UUID) -> int:
    result = await db.execute(
        select(func.count()).where(Like.comment_id == comment_id)
    )
    return result.scalar()


async def create_like(db: AsyncSession, data: dict) -> Like:
    like = Like(**data)
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


async def delete_like(db: AsyncSession, like: Like) -> None:
    await db.delete(like)
    await db.commit()