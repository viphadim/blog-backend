from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.features.users.schemas import UserResponse
# from app.features.categories.schemas import CategoryResponse
# from app.features.tags.schemas import TagResponse


class CreatePostRequest(BaseModel):
    title: str
    content: str
    thumbnail: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: list[str] = []  #  tag names — auto created if not exist


class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    thumbnail: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[list[str]] = None
class CategoryResponse(BaseModel):
    # id:UUID
    name:str 
    slug:str
    description:Optional[str]=None
    # created_at: datetime

    model_config = {"from_attributes": True}
class TagResponse(BaseModel):
    name: str
    slug: str
    # created_at: datetime | None = None

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    content: str
    thumbnail: Optional[str] = None
    is_published: bool
    # user_id: UUID
    # category_id: Optional[UUID] = None
    category: Optional[CategoryResponse] = None
    user: Optional[UserResponse] = None
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
    @classmethod
    def from_post(cls, post) -> "PostResponse":
        return cls(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            thumbnail=post.thumbnail,
            is_published=post.is_published,
            # user_id=post.user_id,
            category_id=post.category_id,
            category=CategoryResponse.model_validate(post.category) if post.category else None,
            # user=UserResponse.model_validate(post.user) if post.user else None,
            tags=[TagResponse.model_validate(pt.tag) for pt in post.tags if pt.tag],  #  post.tags not post.post_tags
            created_at=post.created_at,
            updated_at=post.updated_at,
        )