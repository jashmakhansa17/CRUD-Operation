from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from fastapi import status
from app.main import app
from app.database import get_session, DATABASE_URL
from app.core.dependencies import pwd_context
from app.models.user_model import User
from app.models.blacklistedtoken_model import BlacklistedToken

engine = create_engine(DATABASE_URL, echo=True)


def get_override_session():
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True, scope="function")
def test_db():
    print("****Creating tables****")
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)
    print("****Droping tables****")


app.dependency_overrides[get_session] = get_override_session

client = TestClient(app)


@pytest.fixture()
def session():
    with Session(engine) as session:
        yield session


@pytest.fixture()
def test_admin():
    return {"username": "admin@example.com", "password": "Password@123"}


@pytest.fixture()
def test_login_admin(test_admin, session):
    hashed_password = pwd_context.hash(test_admin["password"])
    user = User(
        email=test_admin["username"],
        full_name="Test Admin",
        hashed_password=hashed_password,
        role="admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/login",
        data={"username": test_admin["username"], "password": test_admin["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def test_user():
    return {"username": "user@example.com", "password": "UserPass@123"}


@pytest.fixture()
def test_login_user(test_user, session):
    hashed_password = pwd_context.hash(test_user["password"])
    user = User(
        email=test_user["username"],
        full_name="Test User",
        hashed_password=hashed_password,
        role="user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    return data["access_token"]
