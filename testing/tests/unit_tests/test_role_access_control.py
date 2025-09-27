import httpx
import pytest

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
            'create': 403,
            'read': 403,
            'update': 403,
            'delete': 403,
        },
        'user': {
            'create': 403,
            'read': 403,
            'update': 403,
            'delete': 403,
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
async def test_role_access_control_crud(auth_header, expected_status_codes):
    """Test role access control CRUD workflow per user."""
    rac_id = 1
    original_data = {
        'role': 'test_role',
        'permissions': ['test.*'],
    }
    new_data = {
        'role': 'test_role',
        'permissions': ['test.read'],
    }

    # Create
    async with httpx.AsyncClient(base_url=API_URL) as client:
        create_response = await client.post('/role_access_controls', json=original_data, headers=auth_header)

    assert create_response.status_code == expected_status_codes['create']
    if create_response.status_code == 200:
        data = create_response.json()
        rac_id = data['id']

    # Verify create
    if create_response.status_code == 200:
        data = create_response.json()
        for k, _ in original_data.items():
            assert original_data[k] == data[k]

    # Get list
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_list_response = await client.get('/role_access_controls', headers=auth_header)

    assert get_list_response.status_code == expected_status_codes['read']

    # Get one
    async with httpx.AsyncClient(base_url=API_URL) as client:
        get_one_response = await client.get(f'/role_access_controls/{rac_id}', headers=auth_header)

    assert get_one_response.status_code == expected_status_codes['read']

    # Update
    async with httpx.AsyncClient(base_url=API_URL) as client:
        update_response = await client.patch(
            f'/role_access_controls/{rac_id}',
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
        delete_response = await client.delete(f'/role_access_controls/{rac_id}', headers=auth_header)

    assert delete_response.status_code == expected_status_codes['delete']

    # Verify delete
    if delete_response.status_code == 200:
        async with httpx.AsyncClient(base_url=API_URL) as client:
            verify_delete_response = await client.get(
                f'/role_access_controls/{rac_id}',
                headers=auth_header
            )
        
        assert verify_delete_response.status_code == 404
