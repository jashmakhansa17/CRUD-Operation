import pytest
from fastapi import status
import uuid


@pytest.mark.usefixtures('setup_auth')
class TestDeleteCategory:

    def test_delete_category_by_user(self):
        category_id = str(uuid.uuid4())
        response = self.client.delete(f'/category/{category_id}', headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_delete_non_exist_category(self):
        category_id = str(uuid.uuid4())
        response = self.client.delete(f'/category/{category_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {category_id} not found'


    def test_delete_category_for_other_user(self,user_data_factory ,category_fixture1):
        user_data = user_data_factory(self.user1_header)
        response = self.client.post(f'/category/user/?user_id={user_data['id']}', json=category_fixture1, headers=self.admin1_header)
        data = response.json()
        TestDeleteCategory.category1_id = data['id']
        assert response.status_code == status.HTTP_200_OK
        
        response = self.client.delete(f'/category/{TestDeleteCategory.category1_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {TestDeleteCategory.category1_id} not found'


    def test_delete_category_for_other_admin(self, category_fixture2):
        response = self.client.post('/category/', json=category_fixture2, headers=self.admin1_header)
        data = response.json()
        TestDeleteCategory.category2_id = data['id']
        assert response.status_code == status.HTTP_200_OK
        
        response = self.client.delete(f'/category/{TestDeleteCategory.category2_id}', headers=self.admin2_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {TestDeleteCategory.category2_id} not found'


    def test_delete_category(self, category_fixture3):
        response = self.client.post('/category/', json=category_fixture3, headers=self.admin1_header)
        data = response.json()
        TestDeleteCategory.category3_id = data['id']
        assert response.status_code == status.HTTP_200_OK
        assert data['name'] == 'category 3'

        response = self.client.get(f'/category/{TestDeleteCategory.category3_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'id' in data
        assert data['name'] == 'category 3'
        assert data['parent_id'] == None

        response = self.client.delete(f'/category/{TestDeleteCategory.category3_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.client.get(f'/category/{TestDeleteCategory.category3_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data['detail'] == f'Category with ID {TestDeleteCategory.category3_id} not found'


    # from this test cases is for '/category/user{user_id}?category_id={category_id}'

    def test_delete_user_category_by_user(self):
        user_id = str(uuid.uuid4())
        category_id = str(uuid.uuid4())
        response = self.client.delete(f'/category/user/{user_id}?category_id={category_id}', headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_delete_user_category_by_admin_for_other_admin(self, user_data_factory, category_fixture4):
        response = self.client.post('/category/', json=category_fixture4, headers=self.admin1_header)
        data = response.json()
        TestDeleteCategory.category4_id = data['id']
        assert response.status_code == status.HTTP_200_OK
        assert data['name'] == 'category 4'


        admin1_data = user_data_factory(self.admin1_header)
        response = self.client.delete(f'/category/user/{admin1_data['id']}?category_id={TestDeleteCategory.category4_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == 'User not found'


    def test_delete_user_category_by_admin_for_current_admin(self, user_data_factory):
        admin1_data = user_data_factory(self.admin1_header)
        response = self.client.delete(f'/category/user/{admin1_data['id']}?category_id={TestDeleteCategory.category4_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == 'User not found'


    def test_delete_user_category_by_admin_for_non_exist_user(self):
        user_id = str(uuid.uuid4())
        category_id = str(uuid.uuid4())

        response = self.client.delete(f'/category/user/{user_id}?category_id={category_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == 'User not found'


    def test_delete_user_category_by_admin_for_exist_user(self,user_data_factory ,category_fixture6):
        user1_data = user_data_factory(self.user1_header)

        response = self.client.post(f'/category/user/?user_id={user1_data['id']}', json=category_fixture6, headers=self.admin1_header)
        data = response.json()
        TestDeleteCategory.category6_id = data['id']

        assert response.status_code == status.HTTP_200_OK
        assert 'id' in data
        
        response = self.client.delete(f'/category/user/{user1_data['id']}?category_id={TestDeleteCategory.category6_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.client.get(f'/category/{TestDeleteCategory.category6_id}', headers=self.user1_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data['detail'] == f'Category with ID {TestDeleteCategory.category6_id} not found'

