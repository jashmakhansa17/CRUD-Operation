from fastapi import status
from .conftest import client


class TestAdmin:
    def test_register_user_success(self, test_login_admin):
        token = test_login_admin

        response = client.post(
            "/registers?role=user",
            json={
                "email": "example1@gmail.com",
                "full_name": "Name1",
                "password": "Password@1",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "example1@gmail.com"
        assert data["full_name"] == "Name1"
        assert data["role"] in ["user", "admin"]
        assert "password" not in data
        assert "id" in data

    def test_register_user_duplicate_email(self, test_login_admin):
        self.test_register_user_success(test_login_admin)
        token = test_login_admin

        response = client.post(
            "/registers?role=user",
            json={
                "email": "example1@gmail.com",
                "full_name": "Duplicate Name",
                "password": "Password@1",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"

    def test_register_user_unauthorized(self):
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
        assert data["detail"] == "Not authenticated"

    def test_get_all_users(self, test_login_admin):
        token = test_login_admin
        response = client.get(
            "/get-all?role=all", headers={"Authorization": f"Bearer {token}"}
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

    def test_get_all_users_filter_by_role_user(self, test_login_admin):
        token = test_login_admin
        response = client.get(
            "/get-all?role=user", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for user in data:
            assert user["role"] == "user"

    def test_get_all_users_filter_by_role_admin(self, test_login_admin):
        token = test_login_admin
        response = client.get(
            "/get-all?role=admin", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for user in data:
            assert user["role"] == "admin"

    def test_get_all_users_limit_and_skip(self, test_login_admin):
        token = test_login_admin
        response = client.get(
            "/get-all?limit=2&skip=1&role=all",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2

    def test_get_all_users_unauthorized(self):
        response = client.get("/get-all")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Not authenticated"


class TestUserRole:
    def test_user_cannot_register_new_user(self, test_login_user):
        token = test_login_user

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

    def test_user_cannot_register_without_token(self):
        response = client.post(
            "/registers?role=user",
            json={
                "email": "newuser@gmail.com",
                "full_name": "New User",
                "password": "Password@1",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_access_all_users(self, test_login_user):
        token = test_login_user
        response = client.get(
            "/get-all?role=all", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_access_admin_users(self, test_login_user):
        token = test_login_user
        response = client.get(
            "/get-all?role=admin", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_use_skip_limit_filters(self, test_login_user):
        token = test_login_user
        response = client.get(
            "/get-all?limit=5&skip=0&role=all",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_get_all_unauthorized(self):
        response = client.get("/get-all")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
