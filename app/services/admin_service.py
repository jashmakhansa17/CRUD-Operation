from fastapi import Depends, HTTPException, status, Query
from typing import Annotated
from sqlmodel import select
from ..models.user_model import User
from ..schemas.user_admin_schema import UserIn, Role
from ..core.dependencies import SessionDep, pwd_context, admin_access


class AdminService:
    def __init__(self, session: SessionDep):
        self.session = session

    def register_user(
        self,
        user: UserIn,
        role: Role,
        current_user: Annotated[User, Depends(admin_access)],
    ):
        existing_user = self.session.exec(
            select(User).where(User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = pwd_context.hash(user.password)
        user_in_db = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=role,
        )

        self.session.add(user_in_db)
        self.session.commit()
        self.session.refresh(user_in_db)
        return user_in_db

    def get_all_users(
        self,
        current_user: Annotated[User, Depends(admin_access)],
        limit: int = Query(default=10, ge=1),
        skip: int = Query(default=0, ge=0),
        role: str = Query(
            enum=["user", "admin", "all"], description="Filter by user role"
        ),
    ):
        if role == "all":
            query = select(User).offset(skip).limit(limit)
        else:
            query = select(User).where(User.role == role).offset(skip).limit(limit)

        users = self.session.exec(query).all()
        return users
