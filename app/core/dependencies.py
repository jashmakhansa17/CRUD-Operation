from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Annotated
from sqlmodel import Session, select
import jwt
from jwt.exceptions import InvalidTokenError
from ..database import get_session
from ..models.user_model import User, Role
from ..models.blacklistedtoken_model import BlacklistedToken
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if data.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: access token required",
            )

        blacklisted = session.exec(
            select(BlacklistedToken).where(
                BlacklistedToken.access_token == data.get("jti")
            )
        ).first()
        if blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted"
            )

        uuid = data.get("uuid")
        if uuid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user = session.exec(select(User).where(User.id == uuid)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


def admin_access(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can access!"
        )
    return current_user
