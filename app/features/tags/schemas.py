from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class CreateTagRequest(BaseModel):
    name: str


class UpdateTagRequest(BaseModel):
    name: Optional[str] = None


class TagResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}

