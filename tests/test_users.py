from fastapi import status
from .conftest import client


def register_user(
    email="test@example.com", password="Test@1234", full_name="Test User"
):
    return client.post(
        "/register",
        json={
            "email": email,
            "full_name": full_name,
            "password": password,
        },
    )


def login_user(email="test@example.com", password="Test@1234"):
    return client.post("/login", data={"username": email, "password": password})


class TestUsers:
    def test_register_user_success(self):
        response = register_user()
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == "user"
        assert "password" not in data
        assert "id" in data

    def test_register_existing_email(self):
        register_user()
        response = register_user()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Email already registered"

    def test_login_invalid_user(self):
        response = client.post(
            "/login", data={"username": "invalid@example.com", "password": "password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid email/user!"

    def test_login_invalid_password(self):
        register_user("pwtest@example.com")
        response = client.post(
            "/login", data={"username": "pwtest@example.com", "password": "password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid password!"

    def test_user_profile_success(self, test_login_user):
        token = test_login_user
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["role"] == "user"
        assert "password" not in data

    def test_admin_profile_fail(self):
        response = client.get("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Not authenticated"
        
    def test_change_password_success(self):
        register_user(email="changepw@example.com", password="OldPass@123")
        login_resp = login_user("changepw@example.com", "OldPass@123")
        token = login_resp.json()["access_token"]
        response = client.post(
            "/change-password?current_password=OldPass@123&new_password=NewPass@123",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password updated successfully"

    def test_change_password_incorrect(self):
        register_user(email="changepw@example.com", password="OldPass@123")
        login_resp = login_user("changepw@example.com", "OldPass@123")
        token = login_resp.json()["access_token"]
        response = client.post(
            "/change-password?current_password=Incorrect@123&new_password=NewPass@123",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Incorrect current password!"

    def test_forgot_password(self):
        register_user("forgot@example.com")
        response = client.post(
            "/forgot-password?email=forgot@example.com"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password reset email sent."

    def test_forgot_password_user_not_found(self):
        register_user("forgot@example.com")
        response = client.post(
            "/forgot-password?email=unknown@example.com"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"


    def test_show_reset_form_success(self):
        register_user(email="reset@example.com", password="OldPass@123")
        login_resp = login_user("reset@example.com", "OldPass@123")
        self.token = login_resp.json()["access_token"]
        response = client.get(f"/reset-password?token={self.token}")
        assert response.status_code == status.HTTP_200_OK

    def test_reset_password_success(self):
        self.test_show_reset_form_success()
        response = client.post(
            "/reset-password", data={"token": self.token, "new_password": "NewPass@123"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password has been reset successfully"

    def test_reset_password_invalid_token(self):
        self.test_show_reset_form_success()
        response = client.post(
            "/reset-password", data={"token": "asdsd-dd", "new_password": "NewPass@123"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Invalid or expired token"

    def test_refresh_token_success(self):
        register_user("abc@example.com")
        login_resp = login_user("abc@example.com")
        refresh_token = login_resp.cookies.get("refresh_token")
        response = client.post(f"/refresh-token?refresh_token={refresh_token}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self):
        register_user("abc@example.com")
        login_resp = login_user("abc@example.com")
        access_token = login_resp.json()["access_token"]
        response = client.post(f"/refresh-token?refresh_token={access_token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid token type: refresh token required"

    def test_refresh_token_blacklistedtoken(self):
        self.test_logout()
        response = client.post(f"/refresh-token?refresh_token={self.refresh_token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Refresh token has been blacklisted"

    def test_logout(self):
        register_user("logout@example.com")
        login_resp = login_user("logout@example.com")
        token = login_resp.json()["access_token"]
        cookies = login_resp.cookies
        self.refresh_token = cookies.get("refresh_token")
        response = client.post(
            "/logout", headers={"Authorization": f"Bearer {token}"}, cookies=cookies
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "logout@example.com is logged out successfully"


def register_user_by_admin(
    token, email="test@example.com", password="Test@1234", full_name="Test User"
):
    return client.post(
        "/register?role=admin",
        json={
            "email": email,
            "full_name": full_name,
            "password": password,
        },
        headers={"Authorization": f"Bearer {token}"},
    )


class TestAdminRole:
    def test_register_user_success(self, test_login_admin):
        token = test_login_admin
        response = register_user_by_admin(token)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == "user"
        assert "password" not in data
        assert "id" in data

    def test_register_existing_user_fails(self, test_login_admin):
        token = test_login_admin
        register_user_by_admin(token)
        response = register_user_by_admin(token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Email already registered"

    def test_login_invalid_user(self):
        response = client.post(
            "/login", data={"username": "invalid@example.com", "password": "password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid email/user!"

    def test_admin_profile_success(self, test_login_admin):
        token = test_login_admin
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "admin@example.com"
        assert data["role"] == "admin"
        assert "password" not in data

    def test_admin_profile_fail(self):
        response = client.get("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_forgot_password(self, test_login_admin):
        token = test_login_admin
        response = client.post(
            "/forgot-password?email=admin@example.com",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password reset email sent."

    def test_forgot_password_user_not_found(self, test_login_admin):
        token = test_login_admin
        response = client.post(
            "/forgot-password?email=unknown@example.com",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"

    def test_change_password_success(self, test_login_admin):
        token = test_login_admin
        response = client.post(
            "/change-password?current_password=Password@123&new_password=NewPass@123",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password updated successfully"

    def test_change_password_incorrect(self, test_login_admin):
        token = test_login_admin
        response = client.post(
            "/change-password?current_password=Incorrect@123&new_password=NewPass@123",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Incorrect current password!"

    def test_show_reset_form_success(self, test_login_admin):
        self.token = test_login_admin
        response = client.get(f"/reset-password?token={self.token}")
        assert response.status_code == status.HTTP_200_OK

    def test_reset_password_success(self, test_login_admin):
        self.test_show_reset_form_success(test_login_admin)
        response = client.post(
            "/reset-password", data={"token": self.token, "new_password": "NewPass@123"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password has been reset successfully"

    def test_reset_password_invalid_token(self, test_login_admin):
        self.test_show_reset_form_success(test_login_admin)
        response = client.post(
            "/reset-password", data={"token": "asdsd-dd", "new_password": "NewPass@123"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Invalid or expired token"

    def test_refresh_token_success(self, test_login_admin):
        token = test_login_admin
        register_user_by_admin(token)
        login_resp = login_user(email="test@example.com", password="Test@1234")
        refresh_token = login_resp.cookies.get("refresh_token")
        response = client.post(f"/refresh-token?refresh_token={refresh_token}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, test_login_admin):
        token = test_login_admin
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid token type: refresh token required"

    def test_refresh_token_blacklistedtoken(self, test_login_admin):
        self.test_logout(test_login_admin)
        response = client.post(f"/refresh-token?refresh_token={self.refresh_token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Refresh token has been blacklisted"

    def test_logout(self, test_login_admin):
        token = test_login_admin
        register_user_by_admin(token)
        login_resp = login_user(email="test@example.com", password="Test@1234")
        token = login_resp.json()["access_token"]
        cookies = login_resp.cookies
        self.refresh_token = login_resp.json()["refresh_token"]
        response = client.post(
            "/logout", headers={"Authorization": f"Bearer {token}"}, cookies=cookies
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "test@example.com is logged out successfully"
