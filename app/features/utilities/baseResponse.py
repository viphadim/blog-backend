from pydantic import BaseModel
from typing import Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    status_code: int
    message: str
    timestamp: datetime
    data: Optional[T] = None
  