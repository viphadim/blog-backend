from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.posts import service
from app.features.posts.schemas import CreatePostRequest, UpdatePostRequest, PostResponse
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user,get_current_user_optional
# from app.core.permissions import can_publish_post
from app.features.users.models import User
from app.core.scopes import Scope

router = APIRouter(prefix="" , tags=['Post'])



@router.get("/posts", response_model=BaseResponse[list[PostResponse]])
async def get_posts(
    category_id: UUID | None = None,
    tag_id: UUID | None = None,
    current_user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    posts= await service.get_all_posts_service(
        db=db,
        current_user=current_user,
        category_id=category_id,
        tag_id=tag_id,
    )
    return BaseResponse(
        success=True, status_code=200, message="Posts retrieved successfully",
        timestamp=datetime.now(),
        data=[PostResponse.from_post(p) for p in posts],
    )

#  Public — but admin/editor sees all
# @router.get("/postss", response_model=BaseResponse[list[PostResponse]])
# async def get_all_posts(
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(get_current_user_optional),  #  optional — no 401 for guests
# ):
#     posts = await service.get_all_posts(db, current_user)
#     return BaseResponse(
#         success=True, status_code=200, message="Posts retrieved successfully",
#         timestamp=datetime.now(),
#         data=[PostResponse.from_post(p) for p in posts],
#     )


#  My posts
# @router.get("/post/me", response_model=BaseResponse[list[PostResponse]])
# async def get_my_posts(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
@router.get("/post/me", response_model=BaseResponse[list[PostResponse]])
async def get_my_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ]),
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
# @router.post("/post", response_model=BaseResponse[PostResponse])
# async def create_post(
#     data: CreatePostRequest,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#   Requires post:create scope
@router.post("/post", response_model=BaseResponse[PostResponse])
async def create_post(
    data: CreatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.POST_CREATE]),  #  
):
    post = await service.create_post(db, current_user, data)
    return BaseResponse(
        success=True, status_code=201, message="Post created successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


# #  Owner, editor, admin
# @router.patch("/post/{post_id}", response_model=BaseResponse[PostResponse])
# async def update_post(
#     post_id: UUID,
#     data: UpdatePostRequest,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#   Requires post:edit_own scope
@router.patch("/post/{post_id}", response_model=BaseResponse[PostResponse])
async def update_post(
    post_id: UUID,
    data: UpdatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.POST_EDIT_OWN]),  #  
):
    post = await service.update_post(db, current_user, post_id, data)
    return BaseResponse(
        success=True, status_code=200, message="Post updated successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


# #  Editor, admin only
# @router.patch("/post/{post_id}/publish", response_model=BaseResponse[PostResponse])
# async def publish_post(
#     post_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(can_publish_post),
# ):

#   Requires post:publish scope
@router.patch("/post/{post_id}/publish", response_model=BaseResponse[PostResponse])
async def publish_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.POST_PUBLISH]),  #  
):
    post = await service.publish_post(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post published successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


# #  Editor, admin only
# @router.patch("/post/{post_id}/unpublish", response_model=BaseResponse[PostResponse])
# async def unpublish_post(
#     post_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(can_publish_post),
# ):
#   Requires post:publish scope
@router.patch("/post/{post_id}/unpublish", response_model=BaseResponse[PostResponse])
async def unpublish_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.POST_PUBLISH]),  #  
):
    post = await service.unpublish_post(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post unpublished successfully",
        timestamp=datetime.now(), data=PostResponse.from_post(post),
    )


# #  Owner or admin
# @router.delete("/post/{post_id}")
# async def delete_post(
#     post_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):

#   Requires post:delete_own scope
@router.delete("/post/{post_id}")
async def delete_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.POST_DELETE_OWN]),  #  
):
    await service.delete_post(db, current_user, post_id)
    return BaseResponse(
        success=True, status_code=200, message="Post deleted successfully",
        timestamp=datetime.now(), data=None,
    )