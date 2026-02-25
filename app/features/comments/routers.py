from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.comments import service
from app.features.comments.schemas import CreateCommentRequest, UpdateCommentRequest, CommentResponse,AllCommentResponse
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user
from app.features.users.models import User

router = APIRouter(prefix="",tags=["Commnent"])

@router.get("/{post_id}/comments", response_model=BaseResponse[list[AllCommentResponse]])
async def get_post_comments(post_id: UUID, db: AsyncSession = Depends(get_db)):
    comments = await service.get_post_comments(db, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Comments retrieved successfully",
        timestamp=datetime.now(),
        data=[AllCommentResponse.from_comment(c) for c in comments],  # ✅
    )

@router.post("/{post_id}/comments", response_model=BaseResponse[CommentResponse])
async def create_comment(
    post_id: UUID,
    data: CreateCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = await service.create_comment(db, current_user, post_id, data)
    return BaseResponse(
        success=True, status_code=201, message="Comment created successfully",
        timestamp=datetime.now(),
        data=CommentResponse.from_comment(comment),  # ✅
    )


# Owner only
@router.patch("/comments/{comment_id}", response_model=BaseResponse[CommentResponse])
async def update_comment(
    comment_id: UUID,
    data: UpdateCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = await service.update_comment(db, current_user, comment_id, data)
    return BaseResponse(
        success=True, status_code=200, message="Comment updated successfully",
        timestamp=datetime.now(),
        data=CommentResponse.model_validate(comment),
    )


# Owner, editor, admin
@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_comment(db, current_user, comment_id)
    return BaseResponse(
        success=True, status_code=200, message="Comment deleted successfully",
        timestamp=datetime.now(), data=None,
    )