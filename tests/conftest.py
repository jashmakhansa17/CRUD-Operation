import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text
from app.main import app
from app.database import get_session
from app.core.config import settings


# Test database engine
test_engine = create_engine(settings.database_url)


# Override get_session dependency to use test DB session
def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


# Create/drop tables once
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    print("****************************CREATING TABLES")
    SQLModel.metadata.create_all(test_engine)
    yield
    print("****************************NOT DELETE TABLES")
    # SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="class")
def client():
    with TestClient(app) as c:
        yield c

    print("**************TRUNCATING TABLES")
    with Session(test_engine) as session:
        session.exec(text("TRUNCATE TABLE category, product RESTART IDENTITY CASCADE;"))
        session.commit()


@pytest.fixture
def get_jwt_token_admin1(client, username="user1@example.com", password="User1@12"):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def get_jwt_token_user1(client, username="user2@example.com", password="User2@12"):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def get_jwt_token_admin2(client, username="user3@example.com", password="User3@12"):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"] 


@pytest.fixture
def get_jwt_token_user2(client, username="user4@example.com", password="User4@12"):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def setup_auth(client, get_jwt_token_admin1, get_jwt_token_admin2, get_jwt_token_user1, get_jwt_token_user2, request):
    request.cls.client = client
    request.cls.admin1_header = {"Authorization": f"Bearer {get_jwt_token_admin1}"}
    request.cls.admin2_header = {"Authorization": f"Bearer {get_jwt_token_admin2}"}
    request.cls.user1_header = {"Authorization": f"Bearer {get_jwt_token_user1}"}
    request.cls.user2_header = {"Authorization": f"Bearer {get_jwt_token_user2}"}


@pytest.fixture
def user_data_factory(client):
    
    def _get_data(user_header):
        response = client.get('/me/',headers = user_header)
        assert response.status_code == status.HTTP_200_OK
        return response.json()
    return _get_data


@pytest.fixture
def category_fixture1():
    return {
        'name':'fake category name for product one',
        'parent_id':None
    }


@pytest.fixture
def category_fixture2():
    return {
        'name':'fake category name for product second'
    }

@pytest.fixture
def category_fixture3():
    return {
        'name':'category 3'
    }

@pytest.fixture
def category_fixture4():
    return {
        'name':'category 4'
    }

@pytest.fixture
def category_fixture5():
    return {
        'name':'category 5'
    }

@pytest.fixture
def category_fixture6():
    return {
        'name':'category 6'
    }

@pytest.fixture
def category_fixture7():
    return {
        'name':'category 7'
    }
