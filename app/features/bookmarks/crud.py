from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from uuid import UUID

from app.features.bookmarks.models import Bookmark
from app.features.posts.models import Post, PostTag
from app.features.users.models import User
from app.features.roles.models import UserRole


async def get_bookmark(db: AsyncSession, user_id: UUID, post_id: UUID) -> Bookmark | None:
    result = await db.execute(
        select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.post_id == post_id)
    )
    return result.scalar_one_or_none()


async def get_user_bookmarks(db: AsyncSession, user_id: UUID) -> list[Bookmark]:
    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .options(
            joinedload(Bookmark.post).options(
                joinedload(Post.user).joinedload(User.user_roles).joinedload(UserRole.role),
                joinedload(Post.category),
                joinedload(Post.tags).joinedload(PostTag.tag),
            )
        )
        .order_by(Bookmark.created_at.desc())
    )
    return result.unique().scalars().all()


async def get_post_bookmarks_count(db: AsyncSession, post_id: UUID) -> int:
    result = await db.execute(
        select(func.count()).where(Bookmark.post_id == post_id)
    )
    return result.scalar()


async def create_bookmark(db: AsyncSession, user_id: UUID, post_id: UUID) -> Bookmark:
    bookmark = Bookmark(user_id=user_id, post_id=post_id)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


async def delete_bookmark(db: AsyncSession, bookmark: Bookmark) -> None:
    await db.delete(bookmark)
    await db.commit()