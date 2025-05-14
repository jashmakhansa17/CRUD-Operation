from fastapi import APIRouter, Depends, BackgroundTasks, Request, Form, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from typing import Annotated
from pydantic import EmailStr
from ..models.user_model import User
from ..schemas.user_admin_schema import UserIn, UserOut, Token
from ..core.dependencies import SessionDep, get_current_user, oauth2_scheme
from ..services.users_service import UserService

router = APIRouter()

@router.post("/register", response_model=UserOut, tags=["all"])
async def register_user(user: UserIn, session: SessionDep):
  return UserService.register_user(user, session) 

@router.post("/login", response_model=Token,tags=["all"])
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, response: Response):
    return UserService.login_user(form_data, session, response)

@router.get("/me", response_model=UserOut,tags=["all"]) 
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.post("/change-password",tags=["all"])
async def change_password(current_password: str,new_password: str,
    current_user: Annotated[User, Depends(get_current_user)],session: SessionDep):
    
    return UserService.change_password(current_password, new_password, current_user, session)

@router.post("/forgot-password",tags=["all"])
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session: SessionDep,
):
    return UserService.forgot_password(email, background_tasks, session)

@router.get("/reset-password", response_class=HTMLResponse, tags=["Not to Use"])
async def show_reset_form(request: Request, token: str):
    return UserService.show_reset_form(request, token)
    
@router.post("/reset-password",tags=["Not to Use"])
async def reset_password(token: Annotated[str, Form(...)],new_password: Annotated[str, Form(...)],session: SessionDep):
    return UserService.reset_password(token, new_password, session)
    
@router.post("/refresh-token", response_model=Token,tags=["all"])
async def refresh_token(refresh_token: str, session: SessionDep):
  
    return UserService.refresh_token(refresh_token, session)
  
@router.post("/logout", tags=["all"])
async def logout(session: SessionDep,current_user: Annotated[User, Depends(get_current_user)],
            request: Request,response: Response,access_token: str = Depends(oauth2_scheme)):
  
  return UserService.logout(session, current_user, request, response, access_token)
  