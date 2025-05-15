from sqlmodel import Session, create_engine
from .core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
