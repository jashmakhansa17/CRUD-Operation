import pytest
from fastapi import status
import uuid


@pytest.mark.usefixtures("setup_auth")
class TestCreateCategory:

    def test_create_data_by_user(self, category_fixture1, get_access_token_for_admin):
        token = login_admin.json()['access_token']
        response = self.client.post(
            "/category/", json=category_fixture1, headers=
        )
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data["detail"] == "Only Admin can access!"

    def test_create_category_successfully(self, category_fixture1, user_data_factory):
        response = self.client.post(
            "/category/", json=category_fixture1, headers=self.admin1_header
        )
        data = response.json()
        TestCreateCategory.category1_id = data["id"]
        user_data = user_data_factory(self.admin1_header)

        assert response.status_code == status.HTTP_200_OK
        assert "id" in data
        assert data["name"] == "category 1"
        assert data["user_id"] == user_data["id"]
        assert data["parent_id"] == None

    def test_create_duplicate_category(self, category_fixture1):
        response = self.client.post(
            "/category/", json=category_fixture1, headers=self.admin1_header
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            data["detail"]
            == "A database integrity error occurred. Please check input and constraints."
        )

    def test_create_category_with_existing_parent(
        self, category_fixture2, user_data_factory
    ):
        response = self.client.post(
            "/category/",
            json={**category_fixture2, "parent_id": TestCreateCategory.category1_id},
            headers=self.admin1_header,
        )
        data = response.json()
        TestCreateCategory.category2_id = data["id"]
        user_data = user_data_factory(self.admin1_header)

        assert response.status_code == status.HTTP_200_OK
        assert "id" in data
        assert data["name"] == "category 2"
        assert data["user_id"] == user_data["id"]
        assert data["parent_id"] == TestCreateCategory.category1_id

    def test_create_category_not_existing_parent(self, category_fixture2):
        response = self.client.post(
            "/category/",
            json={**category_fixture2, "parent_id": str(uuid.uuid4())},
            headers=self.admin1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "Parent id not found"

    def test_create_category_for_user_by_user(self, category_fixture3):
        response = self.client.post(
            f"/category/user/?user_id={str(uuid.uuid4())}",
            json={**category_fixture3},
            headers=self.user1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data["detail"] == "Only Admin can access!"

    def test_create_category_for_user(self, user_data_factory, category_fixture3):
        user_data = user_data_factory(self.user1_header)
        response = self.client.post(
            f"/category/user/?user_id={user_data['id']}",
            json=category_fixture3,
            headers=self.admin1_header,
        )
        data = response.json()
        TestCreateCategory.category3_id = data["id"]

        assert response.status_code == status.HTTP_200_OK
        assert "id" in data
        assert data["name"] == "category 3"
        assert data["user_id"] == user_data["id"]
        assert data["parent_id"] == None

    def test_create_Duplicate_category_for_user(
        self, user_data_factory, category_fixture3
    ):
        user_data = user_data_factory(self.user1_header)
        response = self.client.post(
            f"/category/user/?user_id={user_data['id']}",
            json=category_fixture3,
            headers=self.admin1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            data["detail"]
            == "A database integrity error occurred. Please check your input and constraints."
        )

    def test_create_same_category_for_second_user(
        self, user_data_factory, category_fixture3
    ):
        user_data = user_data_factory(self.user2_header)
        response = self.client.post(
            f"/category/user/?user_id={user_data['id']}",
            json=category_fixture3,
            headers=self.admin1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert "id" in data
        assert data["name"] == "category 3"
        assert data["user_id"] == user_data["id"]
        assert data["parent_id"] == None

    def test_create_child_category_with_other_user_category(
        self, user_data_factory, category_fixture4
    ):
        user_data = user_data_factory(self.user2_header)
        response = self.client.post(
            f"/category/user/?user_id={user_data['id']}",
            json={**category_fixture4, "parent_id": TestCreateCategory.category3_id},
            headers=self.admin1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "Parent id not found"

    def test_create_category_for_non_exist_user(self, category_fixture4):
        response = self.client.post(
            f"/category/user/?user_id={str(uuid.uuid4())}",
            json=category_fixture4,
            headers=self.admin1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "User not found"

    def test_create_category_for_admin(self, user_data_factory, category_fixture4):
        user_data = user_data_factory(self.admin2_header)
        response = self.client.post(
            f"/category/user/?user_id={user_data['id']}",
            json=category_fixture4,
            headers=self.admin1_header,
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "User not found"
