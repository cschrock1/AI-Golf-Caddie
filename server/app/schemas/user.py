from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
