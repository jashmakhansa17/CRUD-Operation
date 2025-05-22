from datetime import datetime, timedelta, timezone
import jwt
from sqlmodel import Session, select
import uuid
from ..models.blacklistedtoken_model import BlacklistedToken
from .config import settings


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "access", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.refresh_token_expire_minutes
    )
    jti = str(uuid.uuid4())
    data.update({"exp": expire, "type": "refresh", "jti": jti})
    encoded_jwt = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_jwt_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_token_expire_minutes
    )
    data.update({"exp": expire, "type": "jwt"})
    encoded_jwt = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def clean_old_tokens(session: Session):
    now = datetime.now(timezone.utc)
    expired_tokens = session.exec(
        select(BlacklistedToken).where(BlacklistedToken.expires_at < now)
    ).all()

    for token in expired_tokens:
        session.delete(token)

    session.commit()
    print(f"message: Cleaned {len(expired_tokens)} expired tokens")
