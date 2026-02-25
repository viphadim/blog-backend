from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.bookmarks import crud
from app.features.bookmarks.schemas import BookmarkStatusResponse
from app.features.users.models import User

from app.features.notifications import service as notification_service
from app.features.posts import crud as post_crud

async def toggle_bookmark(db: AsyncSession, user: User, post_id: UUID) -> BookmarkStatusResponse:
    existing = await crud.get_bookmark(db, user.id, post_id)

    if existing:
        await crud.delete_bookmark(db, existing)
        bookmarked = False
    else:
        await crud.create_bookmark(db, user.id, post_id)
        bookmarked = True

        # Notify post owner
        post = await post_crud.get_post_by_id(db, post_id)
        if post:
            await notification_service.notify_post_bookmarked(db, user.id, post)

    total = await crud.get_post_bookmarks_count(db, post_id)
    return BookmarkStatusResponse(bookmarked=bookmarked, total_bookmarks=total)

async def get_user_bookmarks(db: AsyncSession, user: User):
    return await crud.get_user_bookmarks(db, user.id)


async def get_post_bookmark_status(db: AsyncSession, user: User, post_id: UUID) -> BookmarkStatusResponse:
    existing = await crud.get_bookmark(db, user.id, post_id)
    total = await crud.get_post_bookmarks_count(db, post_id)
    return BookmarkStatusResponse(bookmarked=existing is not None, total_bookmarks=total)