from fastapi import APIRouter, Depends, Query
from typing import Annotated
from ..models.user_model import User
from ..schemas.user_admin_schema import UserIn, UserOut, Role
from ..core.dependencies import SessionDep, admin_access
from ..services.admin_service import AdminService


def get_admin_service(
    session: SessionDep,
) -> AdminService:
    return AdminService(session)


router = APIRouter()


@router.post("/registers", response_model=UserOut, summary="Register a new user/admin")
async def register_user(
    user: UserIn,
    role: Role,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    current_user: Annotated[User, Depends(admin_access)],
):
    return admin_service.register_user(user, role, current_user)


@router.get("/get-all", response_model=list[UserOut], summary="Get all users/admins")
async def get_all_users(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    current_user: Annotated[User, Depends(admin_access)],
    limit: int = Query(default=10, ge=1),
    skip: int = Query(default=0, ge=0),
    role: str = Query(enum=["user", "admin", "all"], description="Filter by user role"),
):
    return admin_service.get_all_users(current_user, limit, skip, role)
