from fastapi import status
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    logout_successful
    
)

class TestLogout:

    def test_logout_success(self, logout_user):
        response=logout_user
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == logout_successful

    def test_logout_invalid_access_token(self, login_user):
        token = login_user.json()["refresh_token"]
        response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_access_token

    def test_logout_unauthorized(self):
        response = client.post(
            "/logout"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == not_authenticated
