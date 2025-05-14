from fastapi import APIRouter, Depends, Query
from typing import Annotated
from ..models.user_model import User
from ..schemas.user_admin_schema import UserIn, UserOut, Role
from ..core.dependencies import SessionDep
from ..core.dependencies import admin_access
from ..services.admin_service import AdminService

router = APIRouter()  

@router.post("/register-first-admin", response_model=UserOut)
async def register_first_admin(user: UserIn, session: SessionDep):
    return AdminService.register_first_admin(user, session)

@router.post("/registers", response_model=UserOut, summary="Register a new user/admin")
async def register_user(user: UserIn, role:Role, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]):
    return AdminService.register_user(user, role, session, current_user)

@router.get("/get-all", response_model=list[UserOut], summary="Get all users/admins")
async def get_all_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(admin_access)],
    limit: int = Query(default=10, ge=1),
    skip: int = Query(default=0, ge=0),
    role: str = Query(enum=["user", "admin", "all"], description="Filter by user role")
):

    return AdminService.get_all_users(session, current_user, limit, skip, role)
