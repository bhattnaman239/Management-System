from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


    class Config:
        from_attributes = True


 