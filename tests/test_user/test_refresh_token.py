from fastapi import status
from ..conftest import client
from app.core.constants import (
    token_is_blacklisted,
    invalid_refresh_token,
    invalid_token
    
)

class TestRefreshToken:


    def test_refresh_token_success(self, login_user):
        token = login_user.json()["refresh_token"]
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid_refresh_token(self, login_user):
        token = login_user.json()["access_token"]
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_refresh_token

    def test_refresh_token_(self):
        response = client.post("/refresh-token?refresh_token=123")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] ==invalid_token

    def test_refresh_token_blacklisted(self, login_user, logout_user):
        token = login_user.json()["refresh_token"]
        assert logout_user.status_code == status.HTTP_200_OK
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == token_is_blacklisted
