from fastapi import status
import pytest
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    token_is_blacklisted,
    email_already_exist,
    password_have_atleast_8_characters,
    password_have_atleast_one_digit,
    password_have_atleast_one_lowercase_letter,
    password_have_atleast_one_special_character,
    password_have_atleast_one_uppercase_letter
)

class TestAdminRegisters:
    def test_register_add_user_success(self, register_user_and_admin_by_admin):
        response=register_user_and_admin_by_admin
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user123@gmail.com"
        assert data["full_name"] == "user name"
        assert data["role"] == "user"
        assert "password" not in data
        assert "id" in data

    def test_register_add_admin_success(self, login_admin):
        token = login_admin.json()["access_token"]

        response = client.post(
            "/registers?role=admin",
            json={
                "email": "admin123@gmail.com",
                "full_name": "admin name",
                "password": "Admin@123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "admin123@gmail.com"
        assert data["full_name"] == "admin name"
        assert data["role"] == "admin"
        assert "password" not in data
        assert "id" in data

    def test_register_user_duplicate_email(self, login_admin, register_user_and_admin_by_admin):
        response=register_user_and_admin_by_admin
        assert response.status_code == status.HTTP_200_OK
        token = login_admin.json()["access_token"]

        response = client.post(
            "/registers?role=user",
            json={
                "email": "user123@gmail.com",
                "full_name": "user2 name",
                "password": "User12@123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == email_already_exist

    def test_register_user_invalid_token(self, login_admin):
        token = login_admin.json()["refresh_token"]

        response = client.post(
            "/registers?role=user",
            json={
                "email": "user123@gmail.com",
                "full_name": "user name",
                "password": "User@123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == invalid_access_token

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
    def test_register_password_validation_errors(self, login_admin, password, output_detail):
        token = login_admin.json()["access_token"]

        response = client.post(
            "/registers?role=user",
            json={
                "email": "user123@gmail.com",
                "full_name": "user name",
                "password": password,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == output_detail

    def test_register_unauthorized(self):
        response = client.post(
            "/registers?role=user",
            json={
                "email": "unauth@gmail.com",
                "full_name": "Unauth User",
                "password": "Password@1",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == not_authenticated

    def test_register_blacklisted(self, login_admin):
        token = login_admin.json()["access_token"]
        client.post("/logout", headers={"Authorization": f"Bearer {token}"})
        response = client.post(
            "/registers?role=user",
            json={
                "email": "user123@gmail.com",
                "full_name": "user name",
                "password": "User@123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == token_is_blacklisted
        
    def test_user_cannot_register_new_user(self, login_user):
        token = login_user.json()["access_token"]

        response = client.post(
            "/registers?role=user",
            json={
                "email": "newuser@gmail.com",
                "full_name": "New User",
                "password": "Password@1",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

