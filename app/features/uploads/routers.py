from fastapi import APIRouter, Depends, UploadFile, File, Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.session import get_db
from app.core.cloudinary import upload_avatar, upload_thumbnail
from app.core.dependencies import get_current_user
from app.core.scopes import Scope
from app.features.users import crud as user_crud
from app.features.users.schemas import UserResponse
from app.utilities.baseResponse import BaseResponse
from app.features.users.models import User

router = APIRouter()


#  Upload user avatar
@router.post("/avatar", response_model=BaseResponse[UserResponse])
async def upload_user_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_WRITE]),
):
    image_url = await upload_avatar(file)

    #  Update user avatar in DB
    updated_user = await user_crud.update_user(db, current_user, {"image_url": image_url})

    return BaseResponse(
        success=True, status_code=200, message="Avatar uploaded successfully",
        timestamp=datetime.now(),
        data=UserResponse.model_validate(updated_user),
    )


#  Upload post thumbnail
@router.post("/thumbnail", response_model=BaseResponse[dict])
async def upload_post_thumbnail(
    file: UploadFile = File(...),
    current_user: User = Security(get_current_user, scopes=[Scope.POST_CREATE]),
):
    image_url = await upload_thumbnail(file)

    return BaseResponse(
        success=True, status_code=200, message="Thumbnail uploaded successfully",
        timestamp=datetime.now(),
        data={"image_url": image_url},  #  return URL to use in create post
    )