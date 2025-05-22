from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session, DATABASE_URL
from app.core.dependencies import pwd_context
from app.models.user_model import User

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
def admin_data():
    return {"username": "admin12@gmail.com","full_name": "admin name","password": "Admin@123"}


@pytest.fixture()
def login_admin(admin_data, session):
    hashed_password = pwd_context.hash(admin_data["password"])
    user = User(
        email=admin_data["username"],
        full_name=admin_data["full_name"],
        hashed_password=hashed_password,
        role="admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/login",
        data={"username": admin_data["username"], "password": admin_data["password"]},
    )
    return response


@pytest.fixture()
def user_data():
    return {"username": "user12@gmail.com","full_name": "user name", "password": "User@123"}


@pytest.fixture()
def login_user(user_data, session):
    hashed_password = pwd_context.hash(user_data["password"])
    user = User(
        email=user_data["username"],
        full_name=user_data["full_name"],
        hashed_password=hashed_password,
        role="user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post(
        "/login",
        data={"username": user_data["username"], "password": user_data["password"]},
    )
    return response

@pytest.fixture()
def register_user_and_admin_by_admin(login_admin):
        token = login_admin.json()["access_token"]

        response = client.post(
            "/registers?role=user",
            json={
                "email": "user123@gmail.com",
                "full_name": "user name",
                "password": "User@123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return response
    
@pytest.fixture()
def register_user():
        response = client.post(
            "/register",
            json={
                "email": "user123@gmail.com",
                "full_name": "user name",
                "password": "User@123",
            },
        )
        return response
    
@pytest.fixture()
def logout_user(login_user):
        token = login_user.json()["access_token"]
        response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
        return response
    
@pytest.fixture()
def logout_admin(login_admin):
        token = login_admin.json()["access_token"]
        response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
        return response