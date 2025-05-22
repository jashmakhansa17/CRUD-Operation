import pytest
from fastapi import status
import uuid


@pytest.mark.usefixtures('setup_auth')
class TestUpdateCategory:
    def test_update_category_by_user(self, category_fixture1):
        category_id = str(uuid.uuid4())
        response = self.client.put(f'/category/{category_id}', json=category_fixture1, headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_update_non_exist_category(self, category_fixture1):
        category_id = str(uuid.uuid4())
        response = self.client.put(f'/category/{category_id}', json=category_fixture1, headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {category_id} not found'


    def test_update_category(self, category_fixture1):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        TestUpdateCategory.category1_id = data['id']
        assert data['name'] == 'category 1'

        response = self.client.put(f'/category/{TestUpdateCategory.category1_id}', json={'name':'category 2'}, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'category 2'


    def test_update_category_duplicate_name(self, category_fixture1, category_fixture3):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post('/category/', json=category_fixture3, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        TestUpdateCategory.category3_id = data['id']

        response = self.client.put(f'/category/{TestUpdateCategory.category3_id}', json={'name':'category 1'}, headers=self.admin1_header)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['detail'] == 'A database integrity error occurred. Please check your input and constraints.'


    # from this test cases is for '/category/user{user_id}?category_id={category_id}'
    
    def test_update_user_category_by_user(self,user_data_factory ,category_fixture1):
        user1_data = user_data_factory(self.user1_header)
        response = self.client.post(f'/category/user/?user_id={user1_data['id']}', json=category_fixture1, headers=self.admin1_header)
        data = response.json()
        TestUpdateCategory.category3_id = data['id']
        assert response.status_code == status.HTTP_200_OK

        response = self.client.put(f'/category/user/{user1_data['id']}?category_id={user1_data['id']}', json=category_fixture1, headers=self.user1_header)
        data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_update_user_category_by_admin(self, user_data_factory, category_fixture6):
        user1_data = user_data_factory(self.user1_header)
        response = self.client.post(f'/category/user/?user_id={user1_data['id']}', json=category_fixture6, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        print('***********----------------',data)
        TestUpdateCategory.category6_id = data['id']
        

        response = self.client.put(f'/category/user/{user1_data['id']}?category_id={TestUpdateCategory.category6_id}', json={'name':'category 7'}, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert data['id'] == TestUpdateCategory.category6_id
        assert data['name'] == 'category 7'