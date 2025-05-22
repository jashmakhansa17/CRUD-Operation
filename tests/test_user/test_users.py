from fastapi import status
from uuid import uuid4
import pytest
from ..conftest import client
from app.core.auth import create_jwt_token, create_access_token


class TestUsers:
    def test_register_user_success(self,register_user):
        response =register_user
        assert response.status_code == status.HTTP_200_OK

        self.data = response.json()
        assert self.data["email"] == "user123@gmail.com"
        assert self.data["full_name"] == "user name"
        assert self.data["role"] == "user"
        assert "password" not in self.data
        assert "id" in self.data

    def test_register_existing_email(self,register_user):
        response=register_user
        assert response.status_code == status.HTTP_200_OK
        response = client.post(
            "/register",
            json={
                "email": "user123@gmail.com",
                "full_name": "user2 name",
                "password": "User123@123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Email already registered"

    @pytest.mark.parametrize(
        "password, output_detail",
        [
            ("User@1", "Password must be at least 8 characters long"),
            ("user@123", "Password must include at least one uppercase letter"),
            ("USER@123", "Password must include at least one lowercase letter"),
            ("User@user", "Password must include at least one digit"),
            ("User123user", "Password must include at least one special character"),
        ]
    )
    def test_register_password_validation_errors(self, password, output_detail):

        response = client.post(
            "/register",
            json={
                "email": "user123@gmail.com",
                "full_name": "user name",
                "password": password,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == output_detail

    def test_login_success(self, login_user):
        response = login_user
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

    def test_login_invalid_user(self,register_user):
        response=register_user
        assert response.status_code == status.HTTP_200_OK
        response = client.post(
            "/login",
            data={"username": "invalid@example.com", "password": "Password@123"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid email/user!"

    def test_login_invalid_password(self,register_user):
        response=register_user
        assert response.status_code == status.HTTP_200_OK
        response = client.post(
            "/login",
            data={"username": "user123@gmail.com", "password": "PASSword@1234"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid password!"

    def test_get_user_success(self, login_user):
        token = login_user.json()["access_token"]

        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user12@gmail.com"
        assert data["full_name"] == "user name"
        assert data["role"] == "user"

    def test_get_user_invalid_token(self, login_user):
        token = login_user.json()["refresh_token"]

        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid token type: access token required"

    def test_get_user_unauthorized(self):
        response = client.get("/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Not authenticated"
        
    def test_get_user_blacklisted(self, login_user, logout_user):
        token = login_user.json()["access_token"]
        assert logout_user.status_code == status.HTTP_200_OK
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Token is blacklisted"

    def test_change_password_success(self, login_user):
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
        assert data["message"] == "Password updated successfully"

    def test_change_password_incorrect_current_password(self, login_user):
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
        assert data["detail"] == "Incorrect current password!"

    def test_change_password_incorrect_confirm_password(self, login_user):
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
        assert data["detail"] == "Confirm password must be same as New password!"

    def test_change_password_invalid_token(self, login_user):
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
        assert data["detail"] == "Invalid token type: access token required"

    @pytest.mark.parametrize(
        "password, output_detail",
        [
            ("User@1", "Password must be at least 8 characters long"),
            ("user@123", "Password must include at least one uppercase letter"),
            ("USER@123", "Password must include at least one lowercase letter"),
            ("User@user", "Password must include at least one digit"),
            ("User123user", "Password must include at least one special character"),
        ]
    )
    def test_change_new_password_validation_errors(self, login_user, password, output_detail):
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

    def test_change_password_unauthorized(self):
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
        assert data["detail"] == "Not authenticated"

    def test_change_password_blacklisted(self, login_user, logout_user):
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
        assert data["detail"] == "Token is blacklisted"
    
    def test_forgot_password_success(self,register_user):
        assert register_user.status_code == status.HTTP_200_OK
        response = client.post("/forgot-password?email=user123@gmail.com")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password reset email sent."

    def test_forgot_password_user_not_found(self):
        response = client.post("/forgot-password?email=unknown@example.com")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"

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
        assert data["message"] == "Password has been reset successfully"

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
        assert data["detail"] == "Invalid or expired token"

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
        assert data["detail"] == "Invalid token type: jwt token required"

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
        assert data["detail"] == "User not found"

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
        assert data["detail"] == "Invalid token: uuid is None"

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
        assert data["detail"] == "Confirm password must be same as New password!"

    @pytest.mark.parametrize(
        "password, output_detail",
        [
            ("User@1", "Password must be at least 8 characters long"),
            ("user@123", "Password must include at least one uppercase letter"),
            ("USER@123", "Password must include at least one lowercase letter"),
            ("User@user", "Password must include at least one digit"),
            ("User123user", "Password must include at least one special character"),
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

    def test_refresh_token_success(self, login_user):
        token = login_user.json()["refresh_token"]
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid_refresh_token(self, login_user):
        token = login_user.json()["access_token"]
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid token type: refresh token required"

    def test_refresh_token_(self):
        response = client.post("/refresh-token?refresh_token=123")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid refresh token"

    def test_refresh_token_blacklisted(self, login_user, logout_user):
        token = login_user.json()["refresh_token"]
        assert logout_user.status_code == status.HTTP_200_OK
        response = client.post(f"/refresh-token?refresh_token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Refresh token has been blacklisted"

    def test_logout_success(self, logout_user):
        response=logout_user
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "user12@gmail.com is logged out successfully"

    def test_logout_invalid_access_token(self, login_user):
        token = login_user.json()["refresh_token"]
        response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid token type: access token required"

    def test_logout_unauthorized(self):
        response = client.post(
            "/logout"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Not authenticated"



# class TestAdminRole:
#     def test_register_user_success(self, test_login_admin):
#         token = test_login_admin
#         response = register_user_by_admin(token)
#         assert response.status_code == status.HTTP_200_OK

#         data = response.json()
#         assert data["email"] == "test@example.com"
#         assert data["full_name"] == "Test User"
#         assert data["role"] == "user"
#         assert "password" not in data
#         assert "id" in data

#     def test_register_existing_user_fails(self, test_login_admin):
#         token = test_login_admin
#         register_user_by_admin(token)
#         response = register_user_by_admin(token)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         data = response.json()
#         assert data["detail"] == "Email already registered"

#     def test_login_invalid_user(self):
#         response = client.post(
#             "/login", data={"username": "invalid@example.com", "password": "password"}
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         data = response.json()
#         assert data["detail"] == "Invalid email/user!"

#     def test_admin_profile_success(self, test_login_admin):
#         token = test_login_admin
#         response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert data["email"] == "admin@example.com"
#         assert data["role"] == "admin"
#         assert "password" not in data

#     def test_admin_profile_fail(self):
#         response = client.get("/me")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         data = response.json()
#         assert data["detail"] == "Not authenticated"

#     def test_forgot_password(self, test_login_admin):
#         token = test_login_admin
#         response = client.post(
#             "/forgot-password?email=admin@example.com",
#             headers={"Authorization": f"Bearer {token}"},
#         )
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert data["message"] == "Password reset email sent."

#     def test_forgot_password_user_not_found(self, test_login_admin):
#         token = test_login_admin
#         response = client.post(
#             "/forgot-password?email=unknown@example.com",
#             headers={"Authorization": f"Bearer {token}"},
#         )
#         assert response.status_code == status.HTTP_404_NOT_FOUND
#         data = response.json()
#         assert data["detail"] == "User not found"

#     def test_change_password_success(self, test_login_admin):
#         token = test_login_admin
#         response = client.post(
#             "/change-password?current_password=Password@123&new_password=NewPass@123",
#             headers={"Authorization": f"Bearer {token}"},
#         )
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert data["message"] == "Password updated successfully"

#     def test_change_password_incorrect(self, test_login_admin):
#         token = test_login_admin
#         response = client.post(
#             "/change-password?current_password=Incorrect@123&new_password=NewPass@123",
#             headers={"Authorization": f"Bearer {token}"},
#         )
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         data = response.json()
#         assert data["detail"] == "Incorrect current password!"

#     def test_show_reset_form_success(self, test_login_admin):
#         self.token = test_login_admin
#         response = client.get(f"/reset-password?token={self.token}")
#         assert response.status_code == status.HTTP_200_OK

#     def test_reset_password_success(self, test_login_admin):
#         self.test_show_reset_form_success(test_login_admin)
#         response = client.post(
#             "/reset-password", data={"token": self.token, "new_password": "NewPass@123"}
#         )
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert data["message"] == "Password has been reset successfully"

#     def test_reset_password_invalid_token(self, test_login_admin):
#         self.test_show_reset_form_success(test_login_admin)
#         response = client.post(
#             "/reset-password", data={"token": "asdsd-dd", "new_password": "NewPass@123"}
#         )
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         data = response.json()
#         assert data["detail"] == "Invalid or expired token"

#     def test_refresh_token_success(self, test_login_admin):
#         token = test_login_admin
#         register_user_by_admin(token)
#         login_resp = login_user(email="test@example.com", password="Test@1234")
#         refresh_token = login_resp.cookies.get("refresh_token")
#         response = client.post(f"/refresh-token?refresh_token={refresh_token}")
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert "access_token" in data
#         assert "refresh_token" in data

#     def test_refresh_token_invalid(self, test_login_admin):
#         token = test_login_admin
#         response = client.post(f"/refresh-token?refresh_token={token}")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         data = response.json()
#         assert data["detail"] == "Invalid token type: refresh token required"

#     def test_refresh_token_blacklistedtoken(self, test_login_admin):
#         self.test_logout(test_login_admin)
#         response = client.post(f"/refresh-token?refresh_token={self.refresh_token}")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         data = response.json()
#         assert data["detail"] == "Refresh token has been blacklisted"

#     def test_logout(self, test_login_admin):
#         token = test_login_admin
#         register_user_by_admin(token)
#         login_resp = login_user(email="test@example.com", password="Test@1234")
#         token = login_resp.json()["access_token"]
#         cookies = login_resp.cookies
#         self.refresh_token = login_resp.json()["refresh_token"]
#         response = client.post(
#             "/logout", headers={"Authorization": f"Bearer {token}"}, cookies=cookies
#         )
#         assert response.status_code == status.HTTP_200_OK
#         data = response.json()
#         assert data["message"] == "test@example.com is logged out successfully"
