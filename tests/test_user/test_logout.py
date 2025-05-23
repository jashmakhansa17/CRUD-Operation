from fastapi import status
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    logout_successful
    
)

class TestLogout:

    def test_logout_success(self, logout_user):
        try:
            response=logout_user
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == logout_successful

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_logout_invalid_access_token(self, login_user):
        try:
            token = login_user.json()["refresh_token"]
            response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_logout_unauthorized(self):
        try:
            response = client.post(
                "/logout"
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == not_authenticated

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_logout_success_by_admin(self, logout_admin):
        try:
            response=logout_admin
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == logout_successful

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_logout_invalid_access_token_by_admin(self, login_admin):
        try:
            token = login_admin.json()["refresh_token"]
            response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token
            
        except Exception:
            logger.error(traceback.format_exc())
            raise