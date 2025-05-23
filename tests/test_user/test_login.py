from fastapi import status
from ..conftest import client
from app.core.constants import (
    invalid_email_or_user,
    invalid_password
    
)

class TestLogin:
  
    def test_login_success(self, login_user):
        response = login_user
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

    def test_login_invalid_user(self,register_user):
        response=register_user
        assert response.status_code == status.HTTP_200_OK
        response = client.post(
            "/login",
            data={"username": "invalid@example.com", "password": "Password@123"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_email_or_user

    def test_login_invalid_password(self,register_user):
        response=register_user
        assert response.status_code == status.HTTP_200_OK
        response = client.post(
            "/login",
            data={"username": "user123@gmail.com", "password": "PASSword@1234"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_password
