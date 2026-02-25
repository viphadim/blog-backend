from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class AllLikeResponse(BaseModel):
    id: UUID
    # user_id: UUID
    post_id: Optional[UUID] = None
    comment_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class LikeResponse(BaseModel):
    id: UUID
    user_id: UUID
    post_id: Optional[UUID] = None
    comment_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LikeStatusResponse(BaseModel):
    liked: bool
    total_likes: int