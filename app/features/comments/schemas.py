from pydantic import BaseModel,EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.features.users.schemas import UserResponse



class CreateCommentRequest(BaseModel):
    content: str
    parent_id: Optional[UUID] = None  # reply to comment


class UpdateCommentRequest(BaseModel):
    content: str

class UserResponse(BaseModel):
    # id: Optional[UUID] = None 
    email: EmailStr
    full_name: Optional[str] = None

    model_config = {"from_attributes": True} 


class CommentResponse(BaseModel):
    # id: UUID
    content: str
    # user_id: UUID
    # post_id: UUID
    parent_id: Optional[UUID] = None
    user: Optional[UserResponse] = None
    replies: list["CommentResponse"] = []  # default empty list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_comment(cls, comment) -> "CommentResponse":
        return cls(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            user=UserResponse.model_validate(comment.user) if comment.user else None,
            replies=[cls.from_comment(r) for r in comment.replies] if comment.replies else [],  # manual
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )


class AllCommentResponse(BaseModel):
    id: UUID
    content: str
    # user_id: UUID
    # post_id: UUID
    parent_id: Optional[UUID] = None
    user: Optional[UserResponse] = None
    replies: list["CommentResponse"] = []  # default empty list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_comment(cls, comment) -> "CommentResponse":
        return cls(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            user=UserResponse.model_validate(comment.user) if comment.user else None,
            replies=[cls.from_comment(r) for r in comment.replies] if comment.replies else [],  # manual
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

AllCommentResponse.model_rebuild()  # required for self-referencing model