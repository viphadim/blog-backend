from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.likes import service
from app.features.likes.schemas import LikeStatusResponse
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user
from app.features.users.models import User
from app.core.scopes import Scope

router = APIRouter()


# # Toggle like/unlike post
# @router.post("/posts/{post_id}/like", response_model=BaseResponse[LikeStatusResponse])
# async def toggle_post_like(
#     post_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
@router.post("/posts/{post_id}/like", response_model=BaseResponse[LikeStatusResponse])
async def toggle_post_like(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ]),  #   any logged in user
):
    result = await service.toggle_post_like(db, current_user, post_id)
    message = "Post liked successfully" if result.liked else "Post unliked successfully"
    return BaseResponse(
        success=True, status_code=200, message=message,
        timestamp=datetime.now(), data=result,
    )


# Get post likes count
@router.get("/posts/{post_id}/like", response_model=BaseResponse[LikeStatusResponse])
async def get_post_likes(post_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await service.get_post_likes(db, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post likes retrieved successfully",
        timestamp=datetime.now(), data=result,
    )


# # Toggle like/unlike comment
# @router.post("/comments/{comment_id}/like", response_model=BaseResponse[LikeStatusResponse])
# async def toggle_comment_like(
#     comment_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
@router.post("/comments/{comment_id}/like", response_model=BaseResponse[LikeStatusResponse])
async def toggle_comment_like(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ]),  #  
):
    result = await service.toggle_comment_like(db, current_user, comment_id)
    message = "Comment liked successfully" if result.liked else "Comment unliked successfully"
    return BaseResponse(
        success=True, status_code=200, message=message,
        timestamp=datetime.now(), data=result,
    )


# Get comment likes count
@router.get("/comments/{comment_id}/like", response_model=BaseResponse[LikeStatusResponse])
async def get_comment_likes(comment_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await service.get_comment_likes(db, comment_id)
    return BaseResponse(
        success=True, status_code=200, message="Comment likes retrieved successfully",
        timestamp=datetime.now(), data=result,
    )