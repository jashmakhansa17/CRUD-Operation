from fastapi import status
import pytest
# from app.core.logers import logger
from .conftest import client


    
class TestUsers:
        
    def test_register_user_success(self,test_login_success):
        token=test_login_success
        response = client.post(
            "/register",
            json={
                "email": "testuser_3@example.com", 
                "full_name": "testname",
                "password": "Test@password1"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["email"] == "testuser_3@example.com"
        assert data["full_name"] == "testname"
        assert data["role"] == "user"
        assert "id" in data
        assert "password" not in data



