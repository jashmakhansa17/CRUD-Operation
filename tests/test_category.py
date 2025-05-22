import pytest
from fastapi import status
import uuid


@pytest.mark.usefixtures('setup_auth')
class TestCreateCategory:


    def test_create_data_by_user(self, category_fixture1):
        response = self.client.post('/category/', json=category_fixture1, headers=self.user1_header)

        data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_create_category(self, category_fixture1, user_data_factory):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        data = response.json()
        TestCreateCategory.category1_id = data['id']
        user_data = user_data_factory(self.admin1_header)

        assert response.status_code == status.HTTP_200_OK
        assert 'id' in data
        assert data['name'] == 'category 1'
        assert data['user_id'] == user_data['id']
        assert data['parent_id'] == None


    def test_create_category_with_existing_parent(self, category_fixture2, user_data_factory):
        response = self.client.post('/category/', json={**category_fixture2,'parent_id':TestCreateCategory.category1_id}, headers=self.admin1_header)
        data = response.json()
        TestCreateCategory.category2_id = data['id']
        user_data = user_data_factory(self.admin1_header)

        assert response.status_code == status.HTTP_200_OK
        assert 'id' in data
        assert data['name'] == 'category 2'
        assert data['user_id'] == user_data['id']
        assert data['parent_id'] == TestCreateCategory.category1_id


    def test_create_category_not_existing_parent(self, category_fixture3):
        response = self.client.post('/category/', json={**category_fixture3,'parent_id':str(uuid.uuid4())}, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data['detail'] == 'A database integrity error occurred. Please check your input and constraints.'
         

    def test_create_duplicate_category(self, category_fixture1):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data['detail'] == 'A database integrity error occurred. Please check your input and constraints.'


    def test_create_category_for_user(self, user_data_factory, category_fixture3):

        user_data = user_data_factory(self.user1_header)

        response = self.client.post(f'/category/user/?user_id={user_data['id']}', json=category_fixture3, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert 'id' in data
        assert data['name'] == 'category 3'
        assert data['user_id'] == user_data['id']
        assert data['parent_id'] == None


    def test_create_category_for_non_exist_user(self, category_fixture4):
        response = self.client.post(f'/category/user/?user_id={str(uuid.uuid4())}', json=category_fixture4, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == 'User not found'


    def test_create_category_for_admin(self, user_data_factory, category_fixture4):
        user_data = user_data_factory(self.admin2_header)
        response = self.client.post(f'/category/user/?user_id={user_data['id']}', json=category_fixture4, headers=self.admin1_header)
        data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == 'User not found'



@pytest.mark.usefixtures('setup_auth')
class TestGetCategory:

    def test_get_empty_category(self):
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

        response = self.client.get('/category/', headers=self.user1_header)
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response.status_code == status.HTTP_200_OK
        assert len(data) > 0


    def test_get_admin_category(self, category_fixture2):
        response = self.client.post('/category/', json=category_fixture2, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get('/category/', headers=self.admin1_header)
        data = response.json()
        TestGetCategory.category_id = data[0]['id']

        assert response.status_code == status.HTTP_200_OK
        assert len(data) > 0

    
    def test_get_all_data_for_admin(self, category_fixture3):
        response = self.client.post('/category/', json=category_fixture3, headers=self.admin1_header)
        response = self.client.get('/category/all/', headers=self.admin1_header)

        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(data) > 0


    def test_get_all_data_for_user(self):
        response = self.client.get('/category/all/', headers=self.user1_header)

        data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'


    def test_get_category_by_pagination(self):
        page = 1
        limit = 1
        response = self.client.get(f'/category/pagination/?page={page}&size={limit}', headers=self.admin1_header)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert len(data) <= limit


    def test_get_category_by_id(self):
        response = self.client.get(f'/category/{TestGetCategory.category_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data['id'] == TestGetCategory.category_id
        assert 'name' in data


    def test_get_empty_category_by_id(self):
        category_id = str(uuid.uuid4())
        response = self.client.get(f'/category/{category_id}', headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {category_id} not found'



@pytest.mark.usefixtures('setup_auth')
class TestUpdateCategory:

    def test_update_non_exist_category(self, category_fixture1):
        category_id = str(uuid.uuid4())
        response = self.client.put(f'/category/{category_id}', json=category_fixture1, headers=self.admin1_header)
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data['detail'] == f'Category with ID {category_id} not found'


    def test_update_category_by_user(self, category_fixture1):
        category_id = str(uuid.uuid4())
        response = self.client.put(f'/category/{category_id}', json=category_fixture1, headers=self.user1_header)
        data = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data['detail'] == 'Only Admin can access!'

    def test_update_category(self, category_fixture1):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        TestUpdateCategory.category_id = data['id']
        assert data['name'] == 'category 1'

        response = self.client.put(f'/category/{TestUpdateCategory.category_id}', json={'name':'category 2'}, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'category 2'


    def test_update_category_duplicate_name(self, category_fixture1, category_fixture3):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post('/category/', json=category_fixture3, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        TestUpdateCategory.category_id = data['id']

        response = self.client.put(f'/category/{TestUpdateCategory.category_id}', json={'name':'category 1'}, headers=self.admin1_header)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['detail'] == 'A database integrity error occurred. Please check your input and constraints.'



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


    def test_delete_category(self, category_fixture1):
        response = self.client.post('/category/', json=category_fixture1, headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        TestDeleteCategory.category_id = data['id']
        assert data['name'] == 'category 1'

        response = self.client.get(f'/category/{TestDeleteCategory.category_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'id' in data
        assert data['name'] == 'category 1'
        assert data['parent_id'] == None

        response = self.client.delete(f'/category/{TestDeleteCategory.category_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = self.client.get(f'/category/{TestDeleteCategory.category_id}', headers=self.admin1_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data['detail'] == f'Category with ID {TestDeleteCategory.category_id} not found'
        
