from fastapi import (
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Form,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from sqlmodel import select
from pydantic import EmailStr
from datetime import timedelta
from ..models.user_model import User
from ..models.blacklistedtoken_model import BlacklistedToken
from ..schemas.user_admin_schema import UserIn
from ..core.dependencies import SessionDep, pwd_context, get_current_user, oauth2_scheme
from ..core.auth import create_access_token, create_refresh_token, clean_old_tokens
from ..utils.send_email import send_reset_email
from ..core.config import settings


class UserService:
    def __init__(self, session: SessionDep):
        self.session = session

    def register_user(self, user: UserIn):
        any_user_exists = self.session.exec(select(User)).first()
        if not any_user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The first user must be an admin.",
            )
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
        current_password: str,
        new_password: str,
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if not pwd_context.verify(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password!",
            )
        UserIn.validate_password(new_password)
        current_user.hashed_password = pwd_context.hash(new_password)
        self.session.add(current_user)
        self.session.commit()
        return {"message": "Password updated successfully"}

    def forgot_password(self, email: EmailStr, background_tasks: BackgroundTasks):
        user = self.session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token_data = {"uuid": str(user.id)}
        reset_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.email_expire_minutes),
        )

        background_tasks.add_task(send_reset_email, email, reset_token)

        return {"message": "Password reset email sent."}

    @staticmethod
    def show_reset_form(request: Request, token: str):
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Reset Your Password</title>
        <style>
            body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            }}
            .container {{
            background: #ffffff;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            width: 100%;
            max-width: 400px;
            }}
            h2 {{
            margin-bottom: 1.5rem;
            color: #333333;
            text-align: center;
            }}
            .form-group {{
            margin-bottom: 1rem;
            }}
            input[type="password"] {{
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1rem;
            box-sizing: border-box;
            transition: border-color 0.2s ease;
            }}
            input[type="password"]:focus {{
            border-color: #007bff;
            outline: none;
            }}
            button {{
            width: 100%;
            padding: 0.75rem;
            background: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s ease;
            }}
            button:hover {{
            background: #0056b3;
            }}
            .note {{
            margin-top: 1rem;
            font-size: 0.875rem;
            color: #666;
            text-align: center;
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <h2>Reset Your Password</h2>
            <form action="/reset-password" method="post">
            <input type="hidden" name="token" value="{token}" />
            <div class="form-group">
                <input
                type="password"
                name="new_password"
                placeholder="Enter your new password"
                required
                />
            </div>
            <button type="submit">Reset Password</button>
            </form>
            <p class="note">This link is valid for {settings.email_expire_minutes} minutes from the time it was requested.</p>
        </div>
        </body>
        </html>
        """

    def reset_password(
        self, token: Annotated[str, Form(...)], new_password: Annotated[str, Form(...)]
    ):
        try:
            data = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            uuid = data.get("uuid")

            if not uuid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
                )

            UserIn.validate_password(new_password)

            user = self.session.exec(select(User).where(User.id == uuid)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            user.hashed_password = pwd_context.hash(new_password)
            self.session.add(user)
            self.session.commit()

            return {"message": "Password has been reset successfully"}

        except InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

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
                    detail="Invalid refresh token",
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
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
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
                    detail="Not a valid refresh token!",
                )

            data_access = jwt.decode(
                access_token, settings.secret_key, algorithms=[settings.algorithm]
            )
            if data_access.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not a valid access token!",
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
