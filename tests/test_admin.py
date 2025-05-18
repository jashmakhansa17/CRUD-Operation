from fastapi import status
from .conftest import client
# from app.core.logers import logger

class TestAdmin:

    def test_register_first_admin_success(self):
        response = client.post(
            "/register-first-admin",
            json={
                "email": "example@gmail.com",
                "full_name": "Name",
                "password": "Password@123", 
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "example@gmail.com"
        assert data["full_name"] == "Name"
        assert data["role"] == "admin"
        assert "password" not in data 
        assert "id" in data

    def test_register_first_admin_already_created(self):
        response = client.post(
            "/register-first-admin",
            json={
                "email": "example@gmail.com",
                "full_name": "Name",
                "password": "Password@123", 
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Initial admin already created"}

    def test_register_user_success(self, test_login_success):
        token = test_login_success

        response = client.post(
            "/registers?role=user",
            json={
                "email": "example1@gmail.com",
                "full_name": "Name1",
                "password": "Password@1"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "example1@gmail.com"
        assert data["full_name"] == "Name1"
        assert data["role"] in ["user", "admin"]
        assert "password" not in data
        assert "id" in data

    def test_register_user_duplicate_email(self, test_login_success):
        token = test_login_success

        response = client.post(
            "/registers?role=user",
            json={
                "email": "example1@gmail.com",
                "full_name": "Duplicate Name",
                "password": "Password@1"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"

    def test_register_user_unauthorized(self):
        response = client.post(
            "/registers?role=user",
            json={
                "email": "unauth@gmail.com",
                "full_name": "Unauth User",
                "password": "Password@1"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_all_users(self, test_login_success):
        token = test_login_success
        response = client.get(
            "/get-all?role=all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 10 
        for user in data:
            assert "id" in user
            assert "email" in user
            assert "full_name" in user
            assert "role" in user
            assert "password" not in user 

    def test_get_all_users_filter_by_role_user(self, test_login_success):
        token = test_login_success
        response = client.get(
            "/get-all?role=user",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for user in data:
            assert user["role"]=="user"

    def test_get_all_users_filter_by_role_admin(self, test_login_success):
        token = test_login_success
        response = client.get(
            "/get-all?role=admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for user in data:
            assert user["role"]=="admin"

    def test_get_all_users_limit_and_skip(self, test_login_success):
        token = test_login_success
        response = client.get(
            "/get-all?limit=2&skip=1&role=all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2

    def test_get_all_users_unauthorized(self):
        response = client.get("/get-all")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
