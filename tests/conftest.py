from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel
from fastapi import status
from app.main import app  
from app.database import engine
client= TestClient(app)

@pytest.fixture(autouse=True,scope="function")
def test_db():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)
    
@pytest.fixture()
def test_user():
    return {"username": "example@gmail.com", "password": "Password@123"}

@pytest.fixture()
def test_login_success(test_user):
        response = client.post(
            "/login",
            data=test_user
        )
        assert response.status_code == status.HTTP_200_OK
        data=response.json()
        token= data["access_token"]
        assert token is not None
        return token