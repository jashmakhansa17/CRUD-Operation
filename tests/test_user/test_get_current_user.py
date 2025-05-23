from fastapi import status
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    token_is_blacklisted    
)


class TestGetCurrentUser:
  

    def test_get_user_success(self, login_user):
        token = login_user.json()["access_token"]

        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user12@gmail.com"
        assert data["full_name"] == "user name"
        assert data["role"] == "user"

    def test_get_user_invalid_token(self, login_user):
        token = login_user.json()["refresh_token"]

        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_access_token

    def test_get_user_unauthorized(self):
        response = client.get("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == not_authenticated
        
    def test_get_user_blacklisted(self, login_user, logout_user):
        token = login_user.json()["access_token"]
        assert logout_user.status_code == status.HTTP_200_OK
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == token_is_blacklisted
