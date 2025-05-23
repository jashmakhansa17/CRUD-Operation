from fastapi import status
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    token_is_blacklisted    
)


class TestGetCurrentUser:
  
    def test_get_user_success(self, login_user):
        try:
            token = login_user.json()["access_token"]

            response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == "user1@gmail.com"
            assert data["full_name"] == "user name"
            assert data["role"] == "user"
        
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_get_user_invalid_token(self, login_user):
        try:
            token = login_user.json()["refresh_token"]

            response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_user_unauthorized(self):
        try:
            response = client.get("/me")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == not_authenticated
        
        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_user_blacklisted(self, login_user, logout_user):
        try:
            token = login_user.json()["access_token"]
            assert logout_user.status_code == status.HTTP_200_OK
            response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == token_is_blacklisted
        
        except Exception:
            logger.error(traceback.format_exc())
            raise
        

class TestGetCurrentAdmin:
  
    def test_get_user_success(self, login_admin):
        try:
            token = login_admin.json()["access_token"]

            response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == "admin1@gmail.com"
            assert data["full_name"] == "admin name"
            assert data["role"] == "admin"

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_user_invalid_token(self, login_admin):
        try:
            token = login_admin.json()["refresh_token"]

            response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_user_unauthorized(self):
        try:
            response = client.get("/me")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == not_authenticated
        
        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_user_blacklisted(self, login_admin, logout_admin):
        try:
            token = login_admin.json()["access_token"]
            assert logout_admin.status_code == status.HTTP_200_OK
            response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == token_is_blacklisted

        except Exception:
            logger.error(traceback.format_exc())
            raise