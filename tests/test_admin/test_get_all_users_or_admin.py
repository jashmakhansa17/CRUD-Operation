from fastapi import status
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    invalid_access_token,
    not_authenticated,
    token_is_blacklisted,
)


class TestGetAllUserAdmin:
    
    def test_get_all_users(self, login_admin):
        try:
            token = login_admin.json()["access_token"]

            response = client.get("/get-all", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) <= 10
            for user_admin in data:
                assert "id" in user_admin
                assert "email" in user_admin
                assert "full_name" in user_admin
                assert "role" in user_admin
                assert "password" not in user_admin
                
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_get_all_users_invalid_token(self, login_admin):
        try:
            login_response = login_admin
            token = login_response.json()["refresh_token"]

            response = client.get("/get-all", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == invalid_access_token
            
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_get_all_users_filter_by_role_user(self, login_admin):
        try:
            token = login_admin.json()["access_token"]

            response = client.get(
                "/get-all?role=user", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            for user in data:
                assert user["role"] == "user"
                
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_get_all_users_filter_by_role_admin(
        self, login_admin, register_admin_by_admin
    ):
        try:
            response = register_admin_by_admin
            assert response.status_code == status.HTTP_200_OK
            token = login_admin.json()["access_token"]

            response = client.get(
                "/get-all?role=admin", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            for admin in data:
                assert admin["role"] == "admin"
                
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_get_all_users_limit_and_skip(self, login_admin):
        try:
            token = login_admin.json()["access_token"]

            response = client.get(
                "/get-all?limit=2&skip=1",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) <= 2

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_all_users_unauthorized(self):
        try:
            response = client.get("/get-all")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == not_authenticated

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_get_all_users_blacklisted(self, login_admin):
        try:
            token = login_admin.json()["access_token"]
            client.post("/logout", headers={"Authorization": f"Bearer {token}"})
            response = client.get("/get-all", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert data["detail"] == token_is_blacklisted

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_user_cannot_access_all_users_and_admin(self, login_user):
        try:
            token = login_user.json()["access_token"]

            response = client.get("/get-all", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_user_cannot_access_all_admin(self, login_user):
        try:
            token = login_user.json()["access_token"]

            response = client.get(
                "/get-all?role=admin", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_user_cannot_access_all_users(self, login_user):
        try:
            token = login_user.json()["access_token"]

            response = client.get(
                "/get-all?role=admin", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_user_cannot_use_skip_limit_filters(self, login_user):
        try:
            token = login_user.json()["access_token"]

            response = client.get(
                "/get-all?limit=5&skip=0",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_user_get_all_unauthorized(self):
        try:
            response = client.get("/get-all")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        except Exception:
            logger.error(traceback.format_exc())
            raise