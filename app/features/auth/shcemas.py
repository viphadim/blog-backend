# from pydantic import BaseModel, EmailStr,field_validator

# class RegisterRequest(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     password: str

#     @field_validator("password")
#     def password_length(cls, v):
#         if len(v.encode("utf-8")) > 72:
#             raise ValueError("Password must be at most 72 characters")
#         return v

# class LoginRequest(BaseModel):
#     email: str
#     password: str

#     @field_validator("password")
#     def password_length(cls, v):
#         if len(v.encode("utf-8")) > 72:
#             raise ValueError("Password too long")
#         return v
    
# class TokenResponse(BaseModel):
#     access_token: str
#     refresh_token: str
#     # token_type: str = "bearer"

# class RefreshTokenRequest(BaseModel):
#     refresh_token: str


from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.features.users.schemas import UserResponse


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("password")
    def password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    # token_type: str = "bearer"
    # user: Optional[UserResponse] = None 


class RefreshTokenRequest(BaseModel):
    refresh_token: str