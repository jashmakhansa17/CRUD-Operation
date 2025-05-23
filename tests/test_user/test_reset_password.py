from fastapi import status
from uuid import uuid4
import pytest
from ..conftest import client
from app.core.auth import create_jwt_token, create_access_token
from app.core.constants import (
    password_have_atleast_8_characters,
    password_have_atleast_one_digit,
    password_have_atleast_one_lowercase_letter,
    password_have_atleast_one_special_character,
    password_have_atleast_one_uppercase_letter,
    password_updated_successful,
    invalid_confirm_password,
    user_not_found,
    invalid_token,
    invalid_jwt_token
    
)

class TestResetPassword:
  

    def test_show_reset_form_success(self):
        user_id = uuid4()
        token = create_jwt_token(data={"uuid": str(user_id)})

        response = client.get(f"/reset-password?token={token}")
        assert response.status_code == status.HTTP_200_OK

    def test_reset_password_success(self,register_user):
        assert register_user.status_code == status.HTTP_200_OK
        user_id = register_user.json()["id"]
        token = create_jwt_token(data={"uuid": str(user_id)})

        response = client.post(
            "/reset-password",
            data={
                "token": token,
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == password_updated_successful

    def test_reset_password_invalid_or_expired_token(self, register_user):
        assert register_user.status_code == status.HTTP_200_OK
        response = client.post(
            "/reset-password",
            data={
                "token": "unknown-token",
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == invalid_token
        
    def test_reset_password_invalid_jwt_token(self, register_user):
        assert register_user.status_code == status.HTTP_200_OK
        user_id = register_user.json()["id"]
        token = create_access_token(data={"uuid": str(user_id)})

        response = client.post(
            "/reset-password",
            data={
                "token": token,
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_jwt_token

    def test_reset_password_user_not_found(self, register_user):
        assert register_user.status_code == status.HTTP_200_OK
        user_id = uuid4()
        token = create_jwt_token(data={"uuid": str(user_id)})

        response = client.post(
            "/reset-password",
            data={
                "token": token,
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == user_not_found

    def test_reset_password_uuid_not_found(self,register_user):
        assert register_user.status_code == status.HTTP_200_OK
        token = create_jwt_token(data={"uuid": ""})

        response = client.post(
            "/reset-password",
            data={
                "token": token,
                "new_password": "NewPass@123",
                "confirm_password": "NewPass@123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == invalid_token

    def test_reset_password_incorrect_password(self, register_user):
        assert register_user.status_code == status.HTTP_200_OK
        user_id = register_user.json()["id"]
        token = create_jwt_token(data={"uuid": str(user_id)})

        response = client.post(
            "/reset-password",
            data={
                "token": token,
                "new_password": "NewPass@123",
                "confirm_password": "New@Pass",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == invalid_confirm_password

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
    def test_reset_new_password_validation_errors(self, register_user, password, output_detail):
        assert register_user.status_code == status.HTTP_200_OK
        user_id = register_user.json()["id"]
        token = create_jwt_token(data={"uuid": str(user_id)})

        response = client.post(
            "/reset-password",
            data={
                "token": token,
                "new_password": password,
                "confirm_password": password,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == output_detail
