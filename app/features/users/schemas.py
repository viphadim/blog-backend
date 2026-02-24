
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    # password: str

class UserRead(BaseModel):
    id: Optional[UUID] = None 
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    phone_number: Optional[str] = None

    class Config:
        orm_mode = True


class updateUserRequest(BaseModel):
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: Optional[UUID] = None 
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    position: Optional[str] = None
    is_approved: Optional[bool] = None
    is_active: Optional[bool] = None
    is_mail_sent: Optional[bool] = None
    is_deleted: Optional[bool] = None
    image_url: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True} 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"