from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.features.comments.models import Comment
from app.features.users.models import User
from app.features.roles.models import UserRole


async def get_post_comments(db: AsyncSession, post_id: UUID) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id, Comment.parent_id == None)
        .options(
            joinedload(Comment.user).joinedload(User.user_roles).joinedload(UserRole.role),
            joinedload(Comment.replies).options(
                joinedload(Comment.user).joinedload(User.user_roles).joinedload(UserRole.role),
                joinedload(Comment.replies).options(  
                    joinedload(Comment.user).joinedload(User.user_roles).joinedload(UserRole.role),
                )
            ),
        )
        .order_by(Comment.created_at.asc())
    )
    return result.unique().scalars().all()


async def get_comment_by_id(db: AsyncSession, comment_id: UUID) -> Comment | None:
    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id)
        .options(
            joinedload(Comment.user).joinedload(User.user_roles).joinedload(UserRole.role),  # ✅
            joinedload(Comment.replies).joinedload(Comment.user).joinedload(User.user_roles).joinedload(UserRole.role),  # ✅
        )
    )
    return result.unique().scalar_one_or_none()


async def create_comment(db: AsyncSession, data: dict) -> Comment:
    comment = Comment(**data)
    db.add(comment)
    await db.commit()

    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment.id)
        .options(
            joinedload(Comment.user).joinedload(User.user_roles).joinedload(UserRole.role),  # ✅
            joinedload(Comment.replies),
        )
    )
    return result.unique().scalar_one()



async def update_comment(db: AsyncSession, comment: Comment, data: dict) -> Comment:
    for key, value in data.items():
        setattr(comment, key, value)
    await db.commit()

    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment.id)
        .options(joinedload(Comment.user), joinedload(Comment.replies))
    )
    return result.unique().scalar_one()


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    await db.delete(comment)
    await db.commit()