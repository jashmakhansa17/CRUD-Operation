from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from uuid import UUID, uuid4
from ..schemas.user_admin_schema import Role


class User(SQLModel, table=True):
    __tablename__ = "people"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    full_name: str
    hashed_password: str
    role: Role
