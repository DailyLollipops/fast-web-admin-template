import httpx
import pytest
from faker import Faker

from testing.fixtures import API_URL, USERS


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
            'create': 401,
            'read': 401,
            'update': 401,
            'delete': 401,
        },
    }
    
    params = []
    for user in USERS:
        expected = ROLE_EXPECTED_STATUS.get(user['role'])
        params.append((user, expected))
    return params


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'auth_header, expected_status_codes',
    get_crud_params(),
    indirect=['auth_header'],
)
async def test_user_crud(auth_header, expected_status_codes):
    """Test user CRUD workflow per user."""
    faker_factory = Faker()
    user_id = 4
    skip_checks = ['password']
    original_data = {
        'name': faker_factory.name(),
        'email': faker_factory.email(),
        'password': 'password'
    }
    new_data = {
        'name': faker_factory.name(),
        'email': faker_factory.email(),
        'password': 'new_password'
    }

    # Create
    async with httpx.AsyncClient(base_url=API_URL) as client:
        create_response = await client.post('/users', json=original_data, headers=auth_header)

    assert create_response.status_code == expected_status_codes['create']
    if create_response.status_code == 200:
        data = create_response.json()
        user_id = data['id']

    # Verify create
    if create_response.status_code == 200:
        data = create_response.json()
        for k, _ in original_data.items():
            if k in skip_checks:
                continue
            assert original_data[k] == data[k]

    # Get list
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_list_response = await client.get('/users', headers=auth_header)

    assert get_list_response.status_code == expected_status_codes['read']

    # Get one
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_one_response = await client.get(f'/users/{user_id}', headers=auth_header)

    assert get_one_response.status_code == expected_status_codes['read']

    # Update
    async with httpx.AsyncClient(base_url=API_URL) as client:
        update_response = await client.patch(f'/users/{user_id}', json=new_data, headers=auth_header)

    assert update_response.status_code == expected_status_codes['update']

    # Verify update
    if update_response.status_code == 200:
        data = update_response.json()
        for k, _ in new_data.items():
            if k in skip_checks:
                continue
            assert new_data[k] == data[k]

    # Delete
    async with httpx.AsyncClient(base_url=API_URL) as client:
        delete_response = await client.delete(f'/users/{user_id}', headers=auth_header)

    assert delete_response.status_code == expected_status_codes['delete']

    # Verify delete
    if delete_response.status_code == 200:
        async with httpx.AsyncClient(base_url=API_URL) as client:
            verify_delete_response = await client.get(f'/users/{user_id}', headers=auth_header)
        
        assert verify_delete_response.status_code == 404
