from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.features.notifications import service
from app.features.notifications.schemas import NotificationResponse, UnreadCountResponse
from app.utilities.baseResponse import BaseResponse
from app.core.dependencies import get_current_user
from app.features.users.models import User
from app.core.scopes import Scope

router = APIRouter()


# @router.get("/", response_model=BaseResponse[list[NotificationResponse]])
# async def get_my_notifications(
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
@router.get("/", response_model=BaseResponse[list[NotificationResponse]])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[Scope.ME_READ]),  #  
):
    notifications = await service.get_my_notifications(db, current_user)
    return BaseResponse(
        success=True, status_code=200, message="Notifications retrieved successfully",
        timestamp=datetime.now(),
        data=[NotificationResponse.from_notification(n) for n in notifications],
    )


@router.get("/unread", response_model=BaseResponse[UnreadCountResponse])
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await service.get_unread_count(db, current_user)
    return BaseResponse(
        success=True, status_code=200, message="Unread count retrieved",
        timestamp=datetime.now(),
        data=UnreadCountResponse(unread_count=count),
    )


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.mark_as_read(db, current_user, notification_id)
    return BaseResponse(
        success=True, status_code=200, message="Notification marked as read",
        timestamp=datetime.now(), data=None,
    )


@router.patch("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.mark_all_as_read(db, current_user)
    return BaseResponse(
        success=True, status_code=200, message="All notifications marked as read",
        timestamp=datetime.now(), data=None,
    )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_notification(db, current_user, notification_id)
    return BaseResponse(
        success=True, status_code=200, message="Notification deleted",
        timestamp=datetime.now(), data=None,
    )