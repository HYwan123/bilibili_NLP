from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    id: Optional[int] = None
    user_id: int
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None  # 'male', 'female', 'other', or 'not_set'
    birth_date: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None