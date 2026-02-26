from fastapi import APIRouter, Depends,Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.tags import service
from app.features.tags.schemas import CreateTagRequest, UpdateTagRequest, TagResponse
from app.utilities.baseResponse import BaseResponse
# from app.core.permissions import can_access_dashboard
from app.core.dependencies import get_current_user
from app.core.scopes import Scope

router = APIRouter(prefix="" , tags=['Tag'])


#  Public
@router.get("/tags", response_model=BaseResponse[list[TagResponse]])
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    tags = await service.get_all_tags(db)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Tags retrieved successfully",
        timestamp=datetime.now(),
        data=[TagResponse.model_validate(t) for t in tags],
    )


#  Public
@router.get("/tag/{tag_id}", response_model=BaseResponse[TagResponse])
async def get_tag(tag_id: UUID, db: AsyncSession = Depends(get_db)):
    tag = await service.get_tag_by_id(db, tag_id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Tag retrieved successfully",
        timestamp=datetime.now(),
        data=TagResponse.model_validate(tag),
    )


#  Admin only
@router.post("/tag", response_model=BaseResponse[TagResponse])
async def create_tag(
    data: CreateTagRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD])
    # current_user=Depends(can_access_dashboard),
):
    tag = await service.create_tag(db, data)
    return BaseResponse(
        success=True,
        status_code=201,
        message="Tag created successfully",
        timestamp=datetime.now(),
        data=TagResponse.model_validate(tag),
    )


#  Admin only
@router.patch("/tag/{tag_id}", response_model=BaseResponse[TagResponse])
async def update_tag(
    tag_id: UUID,
    data: UpdateTagRequest,
    db: AsyncSession = Depends(get_db),
    # current_user=Depends(can_access_dashboard),
    current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD])
):
    tag = await service.update_tag(db, tag_id, data)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Tag updated successfully",
        timestamp=datetime.now(),
        data=TagResponse.model_validate(tag),
    )


#  Admin only
@router.delete("/tag/{tag_id}")
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD])
    # current_user=Depends(can_access_dashboard),
):
    await service.delete_tag(db, tag_id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Tag deleted successfully",
        timestamp=datetime.now(),
        data=None,
    )