from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.features.users.crud import create_user, authenticate_user,get_all_users,get_user_by_id,update_user_imp,delete_user_imp
from app.features.users.schemas import UserCreate, UserRead, Token,UserResponse,updateUserRequest
from app.core.security import create_access_token
from typing import List
from app.features.utilities.baseResponse import BaseResponse
from datetime import datetime

router = APIRouter(prefix="/users", tags=["user"])

@router.post("/register", response_model=BaseResponse[UserResponse])
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    new_user = await create_user(
        db,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number
    )
    return BaseResponse(
        success=True,
        status_code=200,
        message="Create user successfully",
        timestamp=datetime.now(),
        data=new_user,
        
    )


@router.get("", response_model=BaseResponse[list[UserResponse]])
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

@router.get("/{id}", response_model=BaseResponse[UserResponse])
async def get_specific_user(id: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="User retrieved successfully",
        timestamp=datetime.now(),
        data=user,
        
    )


@router.put("/{id}", response_model=BaseResponse[UserResponse])
async def update_user_endpoint(
    id: str,
    user: updateUserRequest, 
    db: AsyncSession = Depends(get_db)
):
    updated_user = await update_user_imp(
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

@router.delete("/{id}", response_model=BaseResponse[None])
async def delete_user(id: str, db: AsyncSession = Depends(get_db)):
    await delete_user_imp(db, id) 
    return BaseResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Deleted user successfully",
        timestamp=datetime.now(),
        data=None,
       
    )