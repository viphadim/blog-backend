from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.likes import crud
from app.features.likes.schemas import LikeStatusResponse
from app.features.users.models import User
from app.utilities.exceptions import NotFoundException
from app.features.posts import crud as post_crud
from app.features.comments import crud as comment_crud
from app.features.notifications import service as notification_service


async def toggle_post_like(db: AsyncSession, user: User, post_id: UUID) -> LikeStatusResponse:
    existing = await crud.get_post_like(db, user.id, post_id)

    if existing:
        await crud.delete_like(db, existing)
        liked = False
    else:
        await crud.create_like(db, {"user_id": user.id, "post_id": post_id, "comment_id": None})
        liked = True

        # Notify post owner
        post = await post_crud.get_post_by_id(db, post_id)
        if post:
            await notification_service.notify_post_liked(db, user.id, post)

    total = await crud.get_post_likes_count(db, post_id)
    return LikeStatusResponse(liked=liked, total_likes=total)


async def toggle_comment_like(db: AsyncSession, user: User, comment_id: UUID) -> LikeStatusResponse:
    existing = await crud.get_comment_like(db, user.id, comment_id)

    if existing:
        await crud.delete_like(db, existing)
        liked = False
    else:
        await crud.create_like(db, {"user_id": user.id, "post_id": None, "comment_id": comment_id})
        liked = True

        # Notify comment owner
        comment = await comment_crud.get_comment_by_id(db, comment_id)
        if comment:
            await notification_service.notify_comment_liked(db, user.id, comment)

    total = await crud.get_comment_likes_count(db, comment_id)
    return LikeStatusResponse(liked=liked, total_likes=total)


async def get_post_likes(db: AsyncSession, post_id: UUID) -> LikeStatusResponse:
    total = await crud.get_post_likes_count(db, post_id)
    return LikeStatusResponse(liked=False, total_likes=total)


async def get_comment_likes(db: AsyncSession, comment_id: UUID) -> LikeStatusResponse:
    total = await crud.get_comment_likes_count(db, comment_id)
    return LikeStatusResponse(liked=False, total_likes=total)