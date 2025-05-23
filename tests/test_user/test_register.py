from fastapi import status
import pytest
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    email_already_exist,
    password_have_atleast_8_characters,
    password_have_atleast_one_digit,
    password_have_atleast_one_lowercase_letter,
    password_have_atleast_one_special_character,
    password_have_atleast_one_uppercase_letter,
   
)

class TestUserRegister:
    
    def test_register_user_success(self,register_user):
        try:
            response =register_user
            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["email"] == "user3@gmail.com"
            assert data["full_name"] == "user name"
            assert data["role"] == "user"
            assert "password" not in data
            assert "id" in data

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_register_existing_email(self,register_user):
        try:
            response=register_user
            assert response.status_code == status.HTTP_200_OK
            response = client.post(
                "/register",
                json={
                    "email": "user3@gmail.com",
                    "full_name": "user2 name",
                    "password": "User123@123",
                },
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == email_already_exist

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
    def test_register_password_validation_errors(self, password, output_detail):
        try:
            response = client.post(
                "/register",
                json={
                    "email": "user2@gmail.com",
                    "full_name": "user name",
                    "password": password,
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["detail"] == output_detail

        except Exception:
            logger.error(traceback.format_exc())
            raise
    