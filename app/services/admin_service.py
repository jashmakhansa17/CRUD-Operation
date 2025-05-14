from fastapi import Depends, HTTPException, status, Query
from typing import Annotated
from sqlmodel import select
from ..models.user_model import User
from ..schemas.user_admin_schema import UserIn, Role
from ..core.dependencies import SessionDep, pwd_context
from ..core.dependencies import admin_access

class AdminService:
    
    @staticmethod
    def register_first_admin(user: UserIn, session: SessionDep):
        existing_user = session.exec(select(User)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Initial admin already created"
            )

        hashed_password = pwd_context.hash(user.password)
        user_in_db = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=Role.admin
        )

        session.add(user_in_db)
        session.commit()
        session.refresh(user_in_db)
        return user_in_db
    
    @staticmethod
    def register_user(user: UserIn, role:Role, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]):
        any_user_exists = session.exec(select(User)).first()
        if not any_user_exists:
            if role != Role.admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The first user must be an admin.register-first-admin endpoint"
                )
        existing_user = session.exec(select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_password = pwd_context.hash(user.password)
        user_in_db = User(
            email=user.email,  
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=role,
            )
        
        session.add(user_in_db)
        session.commit()
        session.refresh(user_in_db)
        return user_in_db
    
    @staticmethod
    def get_all_users(
        session: SessionDep,
        current_user: Annotated[User, Depends(admin_access)],
        limit: int = Query(default=10, ge=1),
        skip: int = Query(default=0, ge=0),
        role: str = Query(enum=["user", "admin", "all"], description="Filter by user role")
    ):

        if role == "all":
            query = select(User).offset(skip).limit(limit)
        else:
            query = select(User).where(User.role == role).offset(skip).limit(limit)

        users = session.exec(query).all()
        return users