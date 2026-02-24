from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
# from app.features.users.crud import get_all_users,update_user,delete_user
from app.features.users.schemas import UserResponse,updateUserRequest
from typing import List
from app.utilities.baseResponse import BaseResponse
from datetime import datetime
from app.core.dependencies import get_current_user
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from app.features.users.service import get_user_by_id,get_all_users,update_user,delete_user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="", tags=["User"])


@router.get("/users", response_model=BaseResponse[list[UserResponse]])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await get_all_users(db)
    
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    
    return BaseResponse(
        success=True,
        status_code=200,
        message="All users retrieved successfully",
        timestamp=datetime.now(),
        data=users,
        
    )



@router.put("/user/{id}", response_model=BaseResponse[UserResponse])
async def update_user_endpoint(
    id: UUID,
    user: updateUserRequest, 
    db: AsyncSession = Depends(get_db)
):
    updated_user = await update_user(
        db,
        id=id,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    return BaseResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Update user successfully",
        timestamp=datetime.now(),
        data=updated_user,
       
    )

@router.delete("/user/{id}", response_model=BaseResponse[None])
async def delete_user_endpoint(id: str, db: AsyncSession = Depends(get_db)):
    await delete_user(db, id) 
    return BaseResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Deleted user successfully",
        timestamp=datetime.now(),
        data=None,
       
    )

@router.get("/user/me", response_model=BaseResponse[UserResponse])
async def read_me(current_user = Depends(get_current_user)):
    return BaseResponse(
        success=True,
        status_code=200,
        message="Current user retrieved successfully",
        timestamp=datetime.now(),
        data=UserResponse.model_validate(current_user),
        # current_user,  
    )


@router.get("/user/{id}", response_model=BaseResponse[UserResponse])
async def get_specific_user(id: UUID, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="User retrieved successfully",
        timestamp=datetime.now(),
        data=user,
        
    )