from fastapi import status
from ..conftest import client
from app.core.constants import (
    password_reset_email_sent,
    user_not_found
    
)
class TestForgotPassword:
  
    
    def test_forgot_password_success(self,register_user):
        assert register_user.status_code == status.HTTP_200_OK
        response = client.post("/forgot-password?email=user123@gmail.com")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == password_reset_email_sent

    def test_forgot_password_user_not_found(self):
        response = client.post("/forgot-password?email=unknown@example.com")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == user_not_found

