from fastapi import APIRouter,Depends,Security
from app.utilities.baseResponse import BaseResponse
from app.features.users.schemas import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.scopes import Scope
# from app.core.permissions import can_access_dashboard
from app.features.roles.service import get_all_roles,get_role_by_id
from app.features.roles.schemas import RoleResponse,RoleWithPermissionsResponse
from datetime import datetime
from uuid import UUID

 
router = APIRouter(prefix="", tags=["Role"])



# @router.get("/roles/permissions", response_model=BaseResponse[list[RoleWithPermissionsResponse]])
# async def get_roles(
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(can_access_dashboard),
# ):
#     roles = await get_all_roles(db)
#     return BaseResponse(
#         success=True,
#         status_code=200,
#         message="Roles retrieved successfully",
#         timestamp=datetime.now(),
#         data=[RoleWithPermissionsResponse.from_role(r) for r in roles],  
#     )

# @router.get("/roles", response_model=BaseResponse[list[RoleResponse]])
# async def get_roles(
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(can_access_dashboard),
# ):
@router.get("/roles", response_model=BaseResponse[list[RoleWithPermissionsResponse]])
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD]),  # ✅
):
    roles = await get_all_roles(db)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Roles retrieved successfully",
        timestamp=datetime.now(),
        data=[RoleResponse.model_validate(r) for r in roles],  
    )

# @router.get("/role/{role_id}", response_model=BaseResponse[RoleWithPermissionsResponse])
# async def get_role(
#     role_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(can_access_dashboard),
# ):
@router.get("/role/{role_id}", response_model=BaseResponse[RoleWithPermissionsResponse])
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD]),  # ✅
):
    role = await get_role_by_id(db, role_id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Role retrieved successfully",
        timestamp=datetime.now(),
        data=RoleWithPermissionsResponse.model_validate(role),
    )