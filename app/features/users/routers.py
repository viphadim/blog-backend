from fastapi import APIRouter, Depends, HTTPException,Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.users import service
from app.features.users.schemas import UserResponse, updateUserRequest,AllUserResponse,UpdateProfileRequest
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user
from app.features.users.models import User
from app.core.scopes import Scope

router = APIRouter(prefix="", tags=["User"])



@router.get("/users", response_model=BaseResponse[list[AllUserResponse]])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await service.get_all_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return BaseResponse(
        success=True,
        status_code=200,
        message="All users retrieved successfully",
        timestamp=datetime.now(),
        data=[AllUserResponse.model_validate(u) for u in users],
    )


# @router.get("/user/me", response_model=BaseResponse[UserResponse])
# async def get_me(current_user: User = Depends(get_current_user)):

@router.get("/users/me", response_model=BaseResponse[AllUserResponse])
async def get_me(
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ])  #  
):
    return BaseResponse(
        success=True,
        status_code=200,
        message="Current user retrieved successfully",
        timestamp=datetime.now(),
        data=AllUserResponse.model_validate(current_user),
    )


# @router.get("/user/{user_id}", response_model=BaseResponse[UserResponse])
# async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):

# @router.patch("/users/{user_id}", response_model=BaseResponse[UserResponse])
# async def update_user(
#     user_id: UUID,
#     data: updateUserRequest,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Security(get_current_user, scopes=[Scope.ME_WRITE]),  #  
# ):
#     user = await service.get_user_by_id(db, user_id)
#     return BaseResponse(
#         success=True,
#         status_code=200,
#         message="User retrieved successfully",
#         timestamp=datetime.now(),
#         data=UserResponse.model_validate(user),
#     )
@router.patch("/profile", response_model=BaseResponse[UserResponse])
async def update_profile(
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_WRITE]),
):
    updated_user = await service.update_profile(db, current_user, data)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Profile updated successfully",
        timestamp=datetime.now(),
        data=UserResponse.model_validate(updated_user),
    )




# @router.patch("/user/{user_id}", response_model=BaseResponse[UserResponse])
# async def update_user(
#     user_id: UUID,
#     data: updateUserRequest,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     updated_user = await service.update_user(db, user_id, data.model_dump(exclude_unset=True))
#     return BaseResponse(
#         success=True,
#         status_code=200,
#         message="User updated successfully",
#         timestamp=datetime.now(),
#         data=UserResponse.model_validate(updated_user),
#     )


@router.delete("/user/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_user(db, user_id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="User deleted successfully",
        timestamp=datetime.now(),
        data=None,
    )