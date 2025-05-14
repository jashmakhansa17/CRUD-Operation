from sqlmodel import SQLModel, Field
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from ..core.config import settings

class BlacklistedToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4,primary_key=True)
    access_token: str = Field(unique=True, index=True)
    refresh_token: str = Field(unique=True, index=True)
    blacklisted_at: datetime = Field(default=datetime.now(timezone.utc))   
    expires_at: datetime = Field(default=datetime.now(timezone.utc) + timedelta(minutes=settings.blacklisted_token_expire_minutes)) 