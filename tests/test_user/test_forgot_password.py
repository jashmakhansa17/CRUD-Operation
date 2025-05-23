from fastapi import status
import traceback
from app.core.loggers import logger
from ..conftest import client
from app.core.constants import (
    password_reset_email_sent,
    user_not_found
    
)
class TestForgotPassword:
  
    
    def test_forgot_password_success(self,register_user):
        try:
            assert register_user.status_code == status.HTTP_200_OK
            response = client.post("/forgot-password?email=user3@gmail.com")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == password_reset_email_sent

        except Exception:
            logger.error(traceback.format_exc())
            raise
        
    def test_forgot_password_user_not_found(self):
        try:
            response = client.post("/forgot-password?email=unknown@example.com")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert data["detail"] == user_not_found
            
        except Exception:
            logger.error(traceback.format_exc())
            raise

    def test_forgot_password_success_by_admin(self,register_admin_by_admin):
        try:
            assert register_admin_by_admin.status_code == status.HTTP_200_OK
            response = client.post("/forgot-password?email=admin2@gmail.com")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == password_reset_email_sent
            
        except Exception:
            logger.error(traceback.format_exc())
            raise