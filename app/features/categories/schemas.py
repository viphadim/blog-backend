from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CreateCategoryRequest(BaseModel):
    name:str
    description:Optional[str]=None


class UpdateCategoryRequest(BaseModel):
    name:str
    description:Optional[str]=None

class CategoryResponse(BaseModel):
    id:UUID
    name:str 
    slug:str
    description:Optional[str]=None
    created_at: datetime

    model_config = {"from_attributes": True}