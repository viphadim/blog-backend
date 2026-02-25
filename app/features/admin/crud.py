from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, date

from app.features.users.models import User
from app.features.posts.models import Post
from app.features.comments.models import Comment
from app.features.likes.models import Like
from app.features.bookmarks.models import Bookmark


async def get_dashboard_stats(db: AsyncSession) -> dict:
    # Total users
    total_users = await db.execute(select(func.count()).select_from(User).where(User.is_deleted == False))

    # Total posts
    total_posts = await db.execute(select(func.count()).select_from(Post))
    total_published = await db.execute(select(func.count()).select_from(Post).where(Post.is_published == True))
    total_unpublished = await db.execute(select(func.count()).select_from(Post).where(Post.is_published == False))

    # Total comments
    total_comments = await db.execute(select(func.count()).select_from(Comment))

    # Total likes
    total_likes = await db.execute(select(func.count()).select_from(Like))

    # Total bookmarks
    total_bookmarks = await db.execute(select(func.count()).select_from(Bookmark))

    # New today
    today = datetime.combine(date.today(), datetime.min.time())
    new_users_today = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= today)
    )
    new_posts_today = await db.execute(
        select(func.count()).select_from(Post).where(Post.created_at >= today)
    )

    return {
        "total_users": total_users.scalar(),
        "total_posts": total_posts.scalar(),
        "total_published_posts": total_published.scalar(),
        "total_unpublished_posts": total_unpublished.scalar(),
        "total_comments": total_comments.scalar(),
        "total_likes": total_likes.scalar(),
        "total_bookmarks": total_bookmarks.scalar(),
        "new_users_today": new_users_today.scalar(),
        "new_posts_today": new_posts_today.scalar(),
    }