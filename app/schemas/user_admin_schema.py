from pydantic import BaseModel, EmailStr, Field as PydanticField, field_validator
from typing import Annotated
from enum import Enum
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
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must include at least one digit")
        if not re.search(r"[@$!%*?&#]", password):
            raise ValueError("Password must include at least one special character")
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
