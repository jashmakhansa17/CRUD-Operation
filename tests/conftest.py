import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.core.config import settings
from app.core.dependencies import pwd_context
from app.models.user_model import User

# Test database engine
test_engine = create_engine(settings.database_url)


def get_override_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = get_override_session


# Create/drop tables once
@pytest.fixture(autouse=True)
def create_test_db():
    print("**CREATING TABLES**")
    SQLModel.metadata.create_all(test_engine)
    yield
    print("**DELETING TABLES**")
    SQLModel.metadata.drop_all(test_engine)


client = TestClient(app)


@pytest.fixture
def session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def user_data_factory():
    def _get_data(token):
        response = client.get("/me/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_200_OK
        return response.json()

    return _get_data


@pytest.fixture()
def admin_data():
    return {
        "username": "admin1@gmail.com",
        "full_name": "admin name",
        "password": "Admin@123",
    }


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
    return {
        "username": "user1@gmail.com",
        "full_name": "user name",
        "password": "User@123",
    }


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
def register_admin_by_admin(login_admin):
    token = login_admin.json()["access_token"]
    response = client.post(
        "/registers?role=admin",
        json={
            "email": "admin2@gmail.com",
            "full_name": "admin name",
            "password": "Admin@123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return response


@pytest.fixture()
def register_user_by_admin(login_admin):
    token = login_admin.json()["access_token"]
    response = client.post(
        "/registers?role=user",
        json={
            "email": "user2@gmail.com",
            "full_name": "user name",
            "password": "User@123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return response

@pytest.fixture
def login_person():
    def _login(username, password):
        response = client.post(
            "/login",
            data={"username": username, "password": password},
        )
        return response.json()['access_token']
    return _login

@pytest.fixture()
def register_user():
    response = client.post(
        "/register",
        json={
            "email": "user3@gmail.com",
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


@pytest.fixture
def get_access_token_for_admin(login_admin):
    return login_admin.json()["access_token"]


@pytest.fixture
def get_access_token_for_user(login_user):
    return login_user.json()["access_token"]


@pytest.fixture
def create_category_for_admin():
    def _create_category(token, category):
        response = client.post(
            "/category/", json=category, headers={"Authorization": f"Bearer {token}"}
        )
        return response

    return _create_category


@pytest.fixture
def create_category_for_user():
    def _create_category(token, user_id, category):
        response = client.post(
            f"/category/user?user_id={user_id}",
            json=category,
            headers={"Authorization": f"Bearer {token}"},
        )
        return response

    return _create_category


@pytest.fixture
def dummy_category_data():
    data = {
        "category_one": {"name": "fake category one"},
        "category_two": {"name": "fake category two"},
    }
    return data
