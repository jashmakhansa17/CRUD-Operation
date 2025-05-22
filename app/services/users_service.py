from fastapi import (
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from sqlmodel import select
from pydantic import EmailStr
from fastapi.templating import Jinja2Templates
from ..models.user_model import User
from ..models.blacklistedtoken_model import BlacklistedToken
from ..schemas.user_admin_schema import UserIn, ForgotPassword, ResetPassword
from ..core.dependencies import SessionDep, pwd_context, get_current_user, oauth2_scheme
from ..core.auth import (
    create_access_token,
    create_refresh_token,
    clean_old_tokens,
    create_jwt_token,
)
from ..utils.send_email import send_reset_email
from ..core.config import settings

templates = Jinja2Templates(directory="app/templates")


class UserService:
    def __init__(self, session: SessionDep):
        self.session = session

    def register_user(self, user: UserIn):
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
            role="user",
        )

        self.session.add(user_in_db)
        self.session.commit()
        self.session.refresh(user_in_db)
        return user_in_db

    def login_user(
        self,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response,
    ):
        user = self.session.exec(
            select(User).where(User.email == form_data.username)
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email/user!"
            )
        if not pwd_context.verify(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password!"
            )
        access_token = create_access_token(data={"uuid": str(user.id)})
        refresh_token = create_refresh_token(data={"uuid": str(user.id)})
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=settings.refresh_token_expire_minutes,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def change_password(
        self,
        password: ForgotPassword,
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if not pwd_context.verify(
            password.current_password, current_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password!",
            )
        UserIn.validate_password(password.new_password)
        if password.new_password != password.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirm password must be same as New password!",
            )
        current_user.hashed_password = pwd_context.hash(password.new_password)
        self.session.add(current_user)
        self.session.commit()
        return {"message": "Password updated successfully"}

    def forgot_password(self, email: EmailStr, background_tasks: BackgroundTasks):
        user = self.session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token_data = {"uuid": str(user.id)}
        reset_token = create_jwt_token(data=token_data)

        background_tasks.add_task(send_reset_email, email, reset_token)

        return {"message": "Password reset email sent."}

    @staticmethod
    def show_reset_form(request: Request, token: str):
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "token": token,
                "expiration_minutes": settings.jwt_token_expire_minutes,
            },
        )

    def reset_password(self, reset: Annotated[ResetPassword, Depends()]):
        try:
            data = jwt.decode(
                reset.token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if data.get("type") != "jwt":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type: jwt token required",
                )

            uuid = data.get("uuid")
            if not uuid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token: uuid is None"
                )

            UserIn.validate_password(reset.new_password)
            if reset.new_password != reset.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirm password must be same as New password!",
                )

            user = self.session.exec(select(User).where(User.id == uuid)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            user.hashed_password = pwd_context.hash(reset.new_password)
            self.session.add(user)
            self.session.commit()

            return {"message": "Password has been reset successfully"}

        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

    def refresh_token(self, refresh_token: str):
        try:
            data = jwt.decode(
                refresh_token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if data.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type: refresh token required",
                )

            blacklisted = self.session.exec(
                select(BlacklistedToken).where(
                    BlacklistedToken.refresh_token == data.get("jti")
                )
            ).first()
            if blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been blacklisted",
                )

            uuid: str = data.get("uuid")
            if uuid is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token: uuid is None",
                )
            user = self.session.exec(select(User).where(User.id == uuid)).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )
            access_token = create_access_token(data={"uuid": str(user.id)})
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

    def logout(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        request: Request,
        response: Response,
        access_token: str = Depends(oauth2_scheme),
    ):
        try:
            refresh_token = request.cookies.get("refresh_token")
            data_refresh = jwt.decode(
                refresh_token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if data_refresh.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type: refresh token required",
                )

            data_access = jwt.decode(
                access_token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if data_access.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type: access token required",
                )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        blacklisted = BlacklistedToken(
            access_token=data_access.get("jti"), refresh_token=data_refresh.get("jti")
        )
        self.session.add(blacklisted)
        self.session.commit()
        response.delete_cookie("refresh_token")
        clean_old_tokens(self.session)
        return {"message": f"{current_user.email} is logged out successfully"}
