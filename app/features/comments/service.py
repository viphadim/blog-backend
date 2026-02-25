from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.features.comments import crud
from app.features.comments.models import Comment
from app.features.comments.schemas import CreateCommentRequest, UpdateCommentRequest
from app.features.users.models import User
from app.utilities.exceptions import NotFoundException, ForbiddenException


async def get_post_comments(db: AsyncSession, post_id: UUID) -> list[Comment]:
    return await crud.get_post_comments(db, post_id)

from app.features.notifications import service as notification_service
from app.features.posts import crud as post_crud

async def create_comment(db: AsyncSession, user: User, post_id: UUID, data: CreateCommentRequest) -> Comment:
    if data.parent_id:
        parent = await crud.get_comment_by_id(db, data.parent_id)
        if not parent:
            raise NotFoundException("Parent comment not found")
        if parent.post_id != post_id:
            raise ForbiddenException("Parent comment does not belong to this post")

    comment = await crud.create_comment(db, {
        "content": data.content,
        "user_id": user.id,
        "post_id": post_id,
        "parent_id": data.parent_id,
    })

    # Notify post owner
    post = await post_crud.get_post_by_id(db, post_id)
    if post:
        await notification_service.notify_post_commented(db, user.id, post)

    # Notify parent comment owner if reply
    if data.parent_id and parent:
        await notification_service.notify_comment_replied(db, user.id, parent)

    return comment
async def update_comment(db: AsyncSession, user: User, comment_id: UUID, data: UpdateCommentRequest) -> Comment:
    comment = await crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise NotFoundException("Comment not found")

    # Only owner can edit — editors/admins can only DELETE not EDIT
    if comment.user_id != user.id:
        raise ForbiddenException("You can only edit your own comments")

    return await crud.update_comment(db, comment, {"content": data.content})



async def delete_comment(db: AsyncSession, user: User, comment_id: UUID) -> None:
    comment = await crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise NotFoundException("Comment not found")

    user_role_names = [ur.role.name for ur in user.user_roles]

    # Owner can delete own comments
    # Editor/admin can delete any comment (moderation)
    if comment.user_id != user.id and not any(r in user_role_names for r in ["author", "admin"]):
        raise ForbiddenException("You don't have permission to delete this comment")

    await crud.delete_comment(db, comment)