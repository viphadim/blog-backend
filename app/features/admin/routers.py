from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.admin import service
from app.features.admin.schemas import DashboardStatsResponse, AssignRoleRequest, MessageResponse
from app.features.users.schemas import UserResponse
from app.features.users import crud as user_crud
from app.utilities.baseResponse import BaseResponse
from app.core.permissions import can_access_dashboard, can_ban_user

router = APIRouter()


# Admin dashboard stats
@router.get("/dashboard", response_model=BaseResponse[DashboardStatsResponse])
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(can_access_dashboard),
):
    stats = await service.get_dashboard_stats(db)
    return BaseResponse(
        success=True, status_code=200, message="Dashboard stats retrieved successfully",
        timestamp=datetime.now(), data=stats,
    )


# Get all users — admin only
@router.get("/users", response_model=BaseResponse[list[UserResponse]])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(can_access_dashboard),
):
    users = await user_crud.get_all_users(db)
    return BaseResponse(
        success=True, status_code=200, message="Users retrieved successfully",
        timestamp=datetime.now(),
        data=[UserResponse.model_validate(u) for u in users],
    )


# Ban user
@router.patch("/users/{user_id}/ban", response_model=BaseResponse[MessageResponse])
async def ban_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(can_ban_user),
):
    await service.ban_user(db, user_id)
    return BaseResponse(
        success=True, status_code=200, message="User banned successfully",
        timestamp=datetime.now(),
        data=MessageResponse(message="User has been banned"),
    )


# Unban user
@router.patch("/users/{user_id}/unban", response_model=BaseResponse[MessageResponse])
async def unban_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(can_ban_user),
):
    await service.unban_user(db, user_id)
    return BaseResponse(
        success=True, status_code=200, message="User unbanned successfully",
        timestamp=datetime.now(),
        data=MessageResponse(message="User has been unbanned"),
    )


# Assign role
@router.patch("/users/{user_id}/assign-role", response_model=BaseResponse[MessageResponse])
async def assign_role(
    user_id: UUID,
    body: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(can_access_dashboard),
):
    await service.assign_role(db, user_id, body.role_name)
    return BaseResponse(
        success=True, status_code=200,
        message=f"Role '{body.role_name}' assigned successfully",
        timestamp=datetime.now(),
        data=MessageResponse(message=f"User is now a {body.role_name}"),
    )


# Revoke role
@router.patch("/users/{user_id}/revoke-role", response_model=BaseResponse[MessageResponse])
async def revoke_role(
    user_id: UUID,
    body: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(can_access_dashboard),
):
    await service.revoke_role(db, user_id, body.role_name)
    return BaseResponse(
        success=True, status_code=200,
        message=f"Role '{body.role_name}' revoked successfully",
        timestamp=datetime.now(),
        data=MessageResponse(message=f"Role has been revoked from user"),
    )