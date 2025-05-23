from fastapi import status
import pytest
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    token_is_blacklisted,
    password_have_atleast_8_characters,
    password_have_atleast_one_digit,
    password_have_atleast_one_lowercase_letter,
    password_have_atleast_one_special_character,
    password_have_atleast_one_uppercase_letter,
    password_updated_successful,
    invalid_current_password,
    invalid_confirm_password
)

class TestChangePasswordByUser:
  
    def test_change_password_success(self, login_user):
        try:        
            token = login_user.json()["access_token"]
            response = client.post(
                "/change-password",
                json={
                    "current_password": "User@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == password_updated_successful
                    
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_change_password_incorrect_current_password(self, login_user):
        try:
            token = login_user.json()["access_token"]
            response = client.post(
                "/change-password?",
                json={
                    "current_password": "User123@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == invalid_current_password

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_incorrect_confirm_password(self, login_user):
        try:
            token = login_user.json()["access_token"]
            response = client.post(
                "/change-password?",
                json={
                    "current_password": "User@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "New@1234",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == invalid_confirm_password

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_invalid_token(self, login_user):
        try:
            token = login_user.json()["refresh_token"]
            response = client.post(
                "/change-password",
                json={
                    "current_password": "User@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    @pytest.mark.parametrize(
        "password, output_detail",
        [
            ("User@1", password_have_atleast_8_characters),
            ("user@123", password_have_atleast_one_uppercase_letter),
            ("USER@123", password_have_atleast_one_lowercase_letter),
            ("User@user", password_have_atleast_one_digit),
            ("User123user", password_have_atleast_one_special_character),
        ]
    )
    def test_change_new_password_validation_errors(self, login_user, password, output_detail):
        try:
            token = login_user.json()["access_token"]

            response = client.post(
                "/change-password",
                json={
                    "current_password": "User@123",
                    "new_password": password,
                    "confirm_password": password,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == output_detail

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_unauthorized(self):
        try:
            response = client.post(
                "/change-password",
                json={
                    "current_password": "User@123",
                    "new_password": "NewPass123",
                    "confirm_password": "NewPass123",
                },
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == not_authenticated

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_blacklisted(self, login_user, logout_user):
        try:
            token = login_user.json()["access_token"]
            assert logout_user.status_code == status.HTTP_200_OK
            response = client.post(
                "/change-password",
                json={
                    "current_password": "User@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == token_is_blacklisted

        except Exception:
            logger.error(traceback.format_exc())
            raise
        

class TestChangePasswordByAdmin:
  
    def test_change_password_success(self, login_admin):
        try:
            token = login_admin.json()["access_token"]
            response = client.post(
                "/change-password",
                json={
                    "current_password": "Admin@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == password_updated_successful
                
        except Exception:
            logger.error(traceback.format_exc())
            raise    

    def test_change_password_incorrect_current_password(self, login_admin):
        try:
            token = login_admin.json()["access_token"]
            response = client.post(
                "/change-password?",
                json={
                    "current_password": "Admin@123@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == invalid_current_password

        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_change_password_incorrect_confirm_password(self, login_admin):
        try:
            token = login_admin.json()["access_token"]
            response = client.post(
                "/change-password?",
                json={
                    "current_password": "Admin@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "New@1234",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == invalid_confirm_password

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_invalid_token(self, login_admin):
        try:
            token = login_admin.json()["refresh_token"]
            response = client.post(
                "/change-password",
                json={
                    "current_password": "Admin@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    @pytest.mark.parametrize(
        "password, output_detail",
        [
            ("User@1", password_have_atleast_8_characters),
            ("user@123", password_have_atleast_one_uppercase_letter),
            ("USER@123", password_have_atleast_one_lowercase_letter),
            ("User@user", password_have_atleast_one_digit),
            ("User123user", password_have_atleast_one_special_character),
        ]
    )
    def test_change_new_password_validation_errors(self, login_admin, password, output_detail):
        try:
            token = login_admin.json()["access_token"]

            response = client.post(
                "/change-password",
                json={
                    "current_password": "Admin@123",
                    "new_password": password,
                    "confirm_password": password,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == output_detail

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_unauthorized(self):
        try:
            response = client.post(
                "/change-password",
                json={
                    "current_password": "User@123",
                    "new_password": "NewPass123",
                    "confirm_password": "NewPass123",
                },
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == not_authenticated

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_change_password_blacklisted(self, login_admin, logout_admin):
        try:
            token = login_admin.json()["access_token"]
            assert logout_admin.status_code == status.HTTP_200_OK
            response = client.post(
                "/change-password",
                json={
                    "current_password": "Admin@123",
                    "new_password": "NewPass@123",
                    "confirm_password": "NewPass@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == token_is_blacklisted

        except Exception:
            logger.error(traceback.format_exc())
            raise