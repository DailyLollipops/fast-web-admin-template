import random

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
            'read': 200,
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
async def test_notification_crud(auth_header, expected_status_codes):
    """Test notification CRUD workflow per user."""
    faker_factory = Faker()
    original_data = {
        'user_id': 3,
        'category': 'info',
        'title': faker_factory.sentence(),
        'body': faker_factory.sentence(),
    }

    new_data = {
        'category': 'info',
        'title': faker_factory.sentence(),
        'body': faker_factory.sentence(),
    }

    # Create
    async with httpx.AsyncClient(base_url=API_URL) as client:
        create_response = await client.post('/notifications', json=original_data, headers=auth_header)

    assert create_response.status_code == expected_status_codes['create']
    if create_response.status_code == 200:
        data = create_response.json()

    # Verify create
    if create_response.status_code == 200:
        data = create_response.json()
        for k, _ in original_data.items():
            assert original_data[k] == data[k]

    # Get list
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_list_response = await client.get('/notifications', headers=auth_header)

    assert get_list_response.status_code == expected_status_codes['read']
    notification_ids = [d.get('id') for d in get_list_response.json().get('data', [])]
    assert len(notification_ids) > 0

    # Get one
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_one_response = await client.get(f'/notifications/{notification_ids[0]}', headers=auth_header)

    assert get_one_response.status_code == expected_status_codes['read']

    # Update
    async with httpx.AsyncClient(base_url=API_URL) as client:
        update_response = await client.patch(
            f'/notifications/{notification_ids[0]}',
            json=new_data,
            headers=auth_header
        )

    assert update_response.status_code == expected_status_codes['update']

    # Verify update
    if update_response.status_code == 200:
        data = update_response.json()
        for k, _ in new_data.items():
            assert new_data[k] == data[k]

    # Delete
    async with httpx.AsyncClient(base_url=API_URL) as client:
        delete_response = await client.delete(f'/notifications/{notification_ids[0]}', headers=auth_header)

    assert delete_response.status_code == expected_status_codes['delete']

    # Verify delete
    if delete_response.status_code == 200:
        async with httpx.AsyncClient(base_url=API_URL) as client:
            verify_delete_response = await client.get(f'/notifications/{notification_ids[0]}', headers=auth_header)
        
        assert verify_delete_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'auth_header',
    USERS,
    indirect=['auth_header'],
)
async def test_notification_not_owner(auth_header):
    """Test to verify a user cannot access another user's notifications."""
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_list_response = await client.get('/notifications', headers=auth_header)

    assert get_list_response.status_code == 200
    notification_ids = [d.get('id') for d in get_list_response.json().get('data', [])]
    assert len(notification_ids) > 0

    for _ in range(10):
        random_list = set(range(1000)) - set(notification_ids)
        random_id = random.choice(list(random_list))

        async with httpx.AsyncClient(base_url=API_URL) as client:
            get_one_response = await client.get(f'/notifications/{random_id}', headers=auth_header)

        assert get_one_response.status_code == 404
