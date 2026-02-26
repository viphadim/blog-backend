from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.bookmarks import service
from app.features.bookmarks.schemas import BookmarkStatusResponse, BookmarkWithPostResponse
from app.features.posts.schemas import PostResponse
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user
from app.features.users.models import User
from app.core.scopes import Scope

router = APIRouter()


# Get my bookmarks
# @router.get("/", response_model=BaseResponse[list[BookmarkWithPostResponse]])
# async def get_my_bookmarks(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
@router.get("/", response_model=BaseResponse[list[BookmarkWithPostResponse]])
async def get_my_bookmarks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ]),  # ✅
):
    bookmarks = await service.get_user_bookmarks(db, current_user)
    return BaseResponse(
        success=True, status_code=200, message="Bookmarks retrieved successfully",
        timestamp=datetime.now(),
        data=[
            BookmarkWithPostResponse(
                id=b.id,
                post_id=b.post_id,
                created_at=b.created_at,
                post=PostResponse.from_post(b.post) if b.post else None,
            )
            for b in bookmarks
        ],
    )


# # Toggle bookmark
# @router.post("/{post_id}", response_model=BaseResponse[BookmarkStatusResponse])
# async def toggle_bookmark(
#     post_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
@router.post("/{post_id}", response_model=BaseResponse[BookmarkStatusResponse])
async def toggle_bookmark(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ]),  # ✅
):
    result = await service.toggle_bookmark(db, current_user, post_id)
    message = "Post bookmarked successfully" if result.bookmarked else "Post unbookmarked successfully"
    return BaseResponse(
        success=True, status_code=200, message=message,
        timestamp=datetime.now(), data=result,
    )


# Get bookmark status for a post
@router.get("/{post_id}/status", response_model=BaseResponse[BookmarkStatusResponse])
async def get_bookmark_status(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await service.get_post_bookmark_status(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Bookmark status retrieved successfully",
        timestamp=datetime.now(), data=result,
    )