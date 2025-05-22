from pydantic import BaseModel, EmailStr, Field as PydanticField, field_validator, ValidationError
from typing import Annotated
from enum import Enum
from fastapi import HTTPException,status, Form, Query
import re
from uuid import UUID


class Role(str, Enum):
    user = "user"
    admin = "admin"


class UserIn(BaseModel):
    
    email: EmailStr
    full_name: Annotated[str, PydanticField(min_length=1)]
    password: str
    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password must include at least one lowercase letter")
        if not re.search(r"\d", password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password must include at least one digit")
        if not re.search(r"[@$!%*?&#]", password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password must include at least one special character")
        return password


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: Role


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ForgotPassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
class ResetPassword():
    def __init__(
        self,
        token: Annotated[str, Form(...)],
        new_password: Annotated[str, Form(...)],
        confirm_password: Annotated[str, Form(...)],
    ):
        self.token = token
        self.new_password = new_password
        self.confirm_password = confirm_password
        
class Filter():
    def __init__(
        self,
        limit:int = Query(default=10, ge=1),
        skip: int = Query(default=0, ge=0),
        role: str = Query(default="all",enum=["user", "admin", "all"], description="Filter by user role")
    ):
        self.limit=limit
        self.skip=skip
        self.role=role
        
class Message(BaseModel):
    message: str
