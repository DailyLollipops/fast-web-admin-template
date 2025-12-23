import pytest
from faker import Faker
from playwright.sync_api import APIRequestContext

from testing.fixtures import USERS


def get_crud_params():
    ROLE_EXPECTED_STATUS = {
        'system': {
            'create': 200,
            'read': 200,
            'update': 200,
            'delete': 200,
        },
        'admin': {
            'create': 200,
            'read': 200,
            'update': 200,
            'delete': 200,
        },
        'user': {
            'create': 403,
            'read': 403,
            'update': 403,
            'delete': 403,
        },
    }
    
    params = []
    for role, _ in USERS.items():
        expected = ROLE_EXPECTED_STATUS[role]
        params.append((role, expected))

    return params


@pytest.mark.parametrize(
    'user_key, expected_status_codes',
    get_crud_params(),
)
def test_user_crud(
    authenticated_api_client,
    user_key: str,
    expected_status_codes: dict[str, int],
):
    """
    Test user CRUD workflow per user role.
    """
    client: APIRequestContext = authenticated_api_client(user_key)
    faker = Faker()

    user_id = 4
    skip_checks = {'password'}

    original_data = {
        'name': faker.name(),
        'email': faker.email(),
        'password': 'password',
    }

    new_data = {
        'name': faker.name(),
        'email': faker.email(),
        'password': 'password',
    }

    # Create
    create_response = client.post(
        '/api/users',
        data=original_data,
    )
    assert create_response.status == expected_status_codes['create']

    if create_response.status == 200:
        data = create_response.json()
        user_id = data['id']

        for k in original_data:
            if k in skip_checks:
                continue
            assert original_data[k] == data[k]

        # Verify login with created user
        login_response = client.post(
            '/api/auth/login',
            form={
                'username': original_data['email'],
                'password': original_data['password'],
            },
        )
        assert login_response.status == 200

    # Get list
    get_list_response = client.get('/api/users')
    assert get_list_response.status == expected_status_codes['read']

    # Get one
    get_one_response = client.get(
        f'/api/users/{user_id}'
    )
    assert get_one_response.status == expected_status_codes['read']

    # Update
    update_response = client.patch(
        f'/api/users/{user_id}',
        data=new_data,
    )
    assert update_response.status == expected_status_codes['update']
    print(update_response.text())

    if update_response.status == 200:
        data = update_response.json()

        for k in new_data:
            if k in skip_checks:
                continue
            assert new_data[k] == data[k]

        # Verify login with updated credentials
        login_response = client.post(
            '/api/auth/login',
            form={
                'username': new_data['email'],
                'password': new_data['password'],
            },
        )
        assert login_response.status == 200, login_response.text()

    # Delete
    delete_response = client.delete(
        f'/api/users/{user_id}'
    )
    assert delete_response.status == expected_status_codes['delete']

    # Verify delete
    if delete_response.status == 200:
        verify_delete_response = client.get(
            f'/api/users/{user_id}'
        )
        assert verify_delete_response.status == 404
