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
            'create': 401,
            'read': 401,
            'update': 401,
            'delete': 401,
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
async def test_application_setting_crud(auth_header, expected_status_codes):
    """Test application setting CRUD workflow per user."""
    faker_factory = Faker()
    application_setting_id = 1
    original_data = {
        'name': faker_factory.name(),
        'value': faker_factory.word(),
    }
    new_data = {
        'name': faker_factory.name(),
        'value': faker_factory.word(),
    }

    # Create
    async with httpx.AsyncClient(base_url=API_URL) as client:
        create_response = await client.post('/application_settings', json=original_data, headers=auth_header)

    assert create_response.status_code == expected_status_codes['create']
    if create_response.status_code == 200:
        data = create_response.json()
        application_setting_id = data['id']

    # Verify create
    if create_response.status_code == 200:
        data = create_response.json()
        for k, _ in original_data.items():
            assert original_data[k] == data[k]

    # Get list
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_list_response = await client.get('/application_settings', headers=auth_header)

    assert get_list_response.status_code == expected_status_codes['read']

    # Get one
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_one_response = await client.get(f'/application_settings/{application_setting_id}', headers=auth_header)

    assert get_one_response.status_code == expected_status_codes['read']

    # Update
    async with httpx.AsyncClient(base_url=API_URL) as client:
        update_response = await client.patch(
            f'/application_settings/{application_setting_id}',
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
        delete_response = await client.delete(f'/application_settings/{application_setting_id}', headers=auth_header)

    assert delete_response.status_code == expected_status_codes['delete']

    # Verify delete
    if delete_response.status_code == 200:
        async with httpx.AsyncClient(base_url=API_URL) as client:
            verify_delete_response = await client.get(
                f'/application_settings/{application_setting_id}',
                headers=auth_header
            )
        
        assert verify_delete_response.status_code == 404
