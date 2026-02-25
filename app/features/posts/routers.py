from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.posts import service
from app.features.posts.schemas import CreatePostRequest, UpdatePostRequest, PostResponse
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user,get_current_user_optional
from app.core.permissions import can_publish_post
from app.features.users.models import User


router = APIRouter(prefix="" , tags=['Post'])



#  Public — but admin/editor sees all
@router.get("/posts", response_model=BaseResponse[list[PostResponse]])
async def get_all_posts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional),  #  optional — no 401 for guests
):
    posts = await service.get_all_posts(db, current_user)
    return BaseResponse(
        success=True, status_code=200, message="Posts retrieved successfully",
        timestamp=datetime.now(),
        data=[PostResponse.from_post(p) for p in posts],
    )

# #  Public
# @router.get("/posts", response_model=BaseResponse[list[PostResponse]])
# async def get_all_posts(db: AsyncSession = Depends(get_db)):
#     posts = await service.get_all_posts(db)
#     return BaseResponse(
#         success=True, status_code=200, message="Posts retrieved successfully",
#         timestamp=datetime.now(),
#         data=[PostResponse.from_post(p) for p in posts],
#     )


#  My posts
@router.get("/post/me", response_model=BaseResponse[list[PostResponse]])
async def get_my_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = await service.get_my_posts(db, current_user.id)
    return BaseResponse(
        success=True, status_code=200, message="Your posts retrieved successfully",
        timestamp=datetime.now(),
        data=[PostResponse.from_post(p) for p in posts],
    )


#  Public — must be before /{post_id}
@router.get("/post/{post_id}", response_model=BaseResponse[PostResponse])
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    post = await service.get_post(db, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post retrieved successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


#  Any logged in user — reader auto → author
@router.post("/post", response_model=BaseResponse[PostResponse])
async def create_post(
    data: CreatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await service.create_post(db, current_user, data)
    return BaseResponse(
        success=True, status_code=201, message="Post created successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


#  Owner, editor, admin
@router.patch("/post/{post_id}", response_model=BaseResponse[PostResponse])
async def update_post(
    post_id: UUID,
    data: UpdatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await service.update_post(db, current_user, post_id, data)
    return BaseResponse(
        success=True, status_code=200, message="Post updated successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


#  Editor, admin only
@router.patch("/post/{post_id}/publish", response_model=BaseResponse[PostResponse])
async def publish_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(can_publish_post),
):
    post = await service.publish_post(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post published successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


#  Editor, admin only
@router.patch("/post/{post_id}/unpublish", response_model=BaseResponse[PostResponse])
async def unpublish_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(can_publish_post),
):
    post = await service.unpublish_post(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post unpublished successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


#  Owner or admin
@router.delete("/post/{post_id}")
async def delete_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_post(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post deleted successfully",
        timestamp=datetime.now(), data=None,
    )