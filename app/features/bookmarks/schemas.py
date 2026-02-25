from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.features.posts.schemas import PostResponse


class BookmarkResponse(BaseModel):
    id: UUID
    user_id: UUID
    post_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class BookmarkStatusResponse(BaseModel):
    bookmarked: bool
    total_bookmarks: int


class BookmarkWithPostResponse(BaseModel):
    id: UUID
    post_id: UUID
    created_at: datetime
    post: Optional[PostResponse] = None

    model_config = {"from_attributes": True}