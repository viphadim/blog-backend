from fastapi import APIRouter,Depends,Security
from app.utilities.baseResponse import BaseResponse
from app.features.categories.schemas import CategoryResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.features.categories.service import get_all_categories
from datetime import datetime
from app.features.categories.schemas import CategoryResponse,CreateCategoryRequest,UpdateCategoryRequest
# from app.core.permissions import can_access_dashboard
from app.features.categories.service import create_category,get_category_by_id,update_category,delete_category
from uuid import UUID
from app.core.dependencies import get_current_user
from app.core.scopes import Scope

router=APIRouter(prefix="",tags=["Category"])

@router.get("/categories", response_model=BaseResponse[list[CategoryResponse]])
async def get_categories(db:AsyncSession=Depends(get_db)):
    result=await get_all_categories(db)
    return BaseResponse(
        success=True,
        status_code=200,
         message="Categories retrieved successfully",
        timestamp=datetime.now(),
        data=result
        # [CategoryResponse.model_validate(r) for r in result]
    )


@router.get("/category/{category_id}", response_model=BaseResponse[CategoryResponse])
async def get_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    category = await get_category_by_id(db, category_id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Category retrieved successfully",
        timestamp=datetime.now(),
        data=CategoryResponse.model_validate(category),
    )


@router.post("/category", response_model=BaseResponse[CategoryResponse])
async def create_a_category(data: CreateCategoryRequest,db: AsyncSession = Depends(get_db),current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD])
                            #  current_user=Depends(can_access_dashboard)
                             ):
    category=await create_category(db,data)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Category created successfully",
        timestamp=datetime.now(),
        data=CategoryResponse.model_validate(category)
    )


@router.patch("/category/{category_id}", response_model=BaseResponse[CategoryResponse])
async def update_a_category(category_id: UUID,data: UpdateCategoryRequest,db: AsyncSession = Depends(get_db) ,current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD])):
    category=await update_category(db,category_id,data)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Category updated successfully",
        timestamp=datetime.now(),
        data=CategoryResponse.model_validate(category),
    )

@router.delete("/{category_id}")
async def delete_a_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
     current_user=Security(get_current_user, scopes=[Scope.ADMIN_DASHBOARD]),
    # current_user=Depends(can_access_dashboard),
):
    await delete_category(db, category_id)
    return BaseResponse(
        success=True,
        status_code=200,
        message="Category deleted successfully",
        timestamp=datetime.now(),
        data=None,
    )