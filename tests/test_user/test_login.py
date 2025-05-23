from fastapi import status
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    invalid_email_or_user,
    invalid_password
    
)

class TestLoginByUser:
  
    def test_login_success(self, login_user):
        try:
            response = login_user
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert "token_type" in data

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_login_invalid_user(self,register_user):
        try:
            response=register_user
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/login",
                data={"username": "invalid@example.com", "password": "Password@123"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_email_or_user

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_login_invalid_password(self,register_user):
        try:
            response=register_user
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/login",
                data={"username": "user3@gmail.com", "password": "PASSword@1234"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_password

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
        
class TestLoginByAdmin:
  
    def test_login_success(self, login_admin):
        try:
            response = login_admin
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert "token_type" in data

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_login_invalid_user(self,register_user_by_admin):
        try:
            response=register_user_by_admin
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/login",
                data={"username": "invalid@example.com", "password": "Password@123"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_email_or_user
        
        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_login_invalid_admin(self,register_admin_by_admin):
        try:
            response=register_admin_by_admin
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/login",
                data={"username": "invalid@example.com", "password": "Password@123"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_email_or_user

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_login_invalid_user_password(self,register_user_by_admin):
        try:
            response=register_user_by_admin
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/login",
                data={"username": "user2@gmail.com", "password": "PASSword@1234"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_password

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_login_invalid_admin_password(self,register_admin_by_admin):
        try:
            response=register_admin_by_admin
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/login",
                data={"username": "admin2@gmail.com", "password": "PASSword@1234"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_password

        except Exception:
            logger.error(traceback.format_exc())
            raise