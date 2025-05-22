import pytest
from fastapi import status
import uuid


@pytest.mark.usefixtures('setup_auth')
class TestGetCategory:

    def test_get_empty_category_for_admin(self):
        response = self.client.get('/category/', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data == []


    def test_get_empty_categoryfor_user(self):
        response = self.client.get('/category/', headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data == []


    def test_get_user_category(self, category_fixture1, user_data_factory):
        user_data = user_data_factory(self.user1_header)
        response = self.client.post(f'/category/user/?user_id={user_data['id']}', json=category_fixture1, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get('/category/', headers=self.user1_header)
        data = response.json()
        TestGetCategory.category1_id = data[0]['id']

        assert response.status_code == status.HTTP_200_OK
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'user_id' in data[0]
        assert 'parent_id' in data[0]


    def test_get_admin_category(self, category_fixture2):
        response = self.client.post('/category/', json=category_fixture2, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get('/category/', headers=self.admin1_header)
        data = response.json()
        TestGetCategory.category2_id = data[0]['id']

        assert response.status_code == status.HTTP_200_OK
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'user_id' in data[0]
        assert 'parent_id' in data[0]

    
    def test_get_all_data_by_admin(self, category_fixture3):
        response = self.client.post('/category/', json=category_fixture3, headers=self.admin1_header)
        response = self.client.get('/category/all/', headers=self.admin1_header)

        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'user_id' in data[0]
        assert 'parent_id' in data[0]


    def test_get_all_data_by_user(self):
        response = self.client.get('/category/all/', headers=self.user1_header)

        data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_get_category_by_pagination_by_admin(self):
        page = 1
        limit = 1
        response = self.client.get(f'/category/pagination/?page={page}&size={limit}', headers=self.admin1_header)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert len(data) <= limit


    def test_get_category_by_pagination_by_user(self):
        page = 1
        limit = 1
        response = self.client.get(f'/category/pagination/?page={page}&size={limit}', headers=self.user1_header)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert len(data) <= limit


    def test_get_empty_category_by_pagination_by_admin(self):
        page = 1
        limit = 1
        response = self.client.get(f'/category/pagination/?page={page}&size={limit}', headers=self.admin2_header)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert data == []


    def test_get_empty_category_by_pagination_by_user(self):
        page = 1
        limit = 1
        response = self.client.get(f'/category/pagination/?page={page}&size={limit}', headers=self.user2_header)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert data == []


    def test_get_empty_category_by_id(self):
        category_id = str(uuid.uuid4())
        response = self.client.get(f'/category/{category_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {category_id} not found'


    def test_get_category_by_id_by_user(self):
        response = self.client.get(f'/category/{TestGetCategory.category1_id}', headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data['id'] == TestGetCategory.category1_id
        assert 'name' in data
        assert 'user_id' in data
        assert 'parent_id' in data


    def test_get_category_by_id_by_admin(self):
        response = self.client.get(f'/category/{TestGetCategory.category2_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data['id'] == TestGetCategory.category2_id
        assert 'name' in data
        assert 'user_id' in data
        assert 'parent_id' in data


    def test_get_empty_nested_category_by_user(self):
        category_id = str(uuid.uuid4())
        response = self.client.get(f'/category/nested/{category_id}/', headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f"Category with ID {category_id} not found"

    
    def test_get_empty_nested_category_by_admin(self):
        category_id = str(uuid.uuid4())
        response = self.client.get(f'/category/nested/{category_id}/', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f"Category with ID {category_id} not found"
        


    def test_get_nested_category_by_user(self, category_fixture5, category_fixture6, category_fixture7):
        # response = self.client.get(f'/category/nested/{TestGetCategory.category1_id}/', headers=self.user1_header)
        # data = response.json()
        # assert response.status_code == status.HTTP_200_OK


        response = self.client.post('/category/', json=category_fixture5, headers=self.admin1_header)
        data = response.json()
        TestGetCategory.category5_id = data['id']
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post('/category/', json={**category_fixture6, 'parent_id':data['id']}, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post('/category/', json={**category_fixture7, 'parent_id':data['id']}, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get(f'/category/nested/{TestGetCategory.category5_id}/', headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK

        assert 'id' in data
        assert 'name' in data
        assert 'user_id' in data
        assert 'parent_id' in data
        assert  'subcategories' in data
        assert len(data['subcategories']) >= 0