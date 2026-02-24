from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PageResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    data: List[T]