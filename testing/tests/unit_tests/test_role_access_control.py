import pytest
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
    for role, _ in USERS.items():
        expected = ROLE_EXPECTED_STATUS[role]
        params.append((role, expected))

    return params


@pytest.mark.parametrize(
    'user_key, expected_status_codes',
    get_crud_params(),
)
def test_role_access_control_crud(
    authenticated_api_client,
    user_key: str,
    expected_status_codes: dict[str, int],
):
    """
    Test role access control CRUD workflow per user role.
    """
    client: APIRequestContext = authenticated_api_client(user_key)

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
    create_response = client.post(
        '/api/role_access_controls',
        data=original_data,
    )
    assert create_response.status == expected_status_codes['create']

    if create_response.status == 200:
        data = create_response.json()
        rac_id = data['id']

        for k in original_data:
            assert original_data[k] == data[k]

    # Get list
    get_list_response = client.get('/api/role_access_controls')
    assert get_list_response.status == expected_status_codes['read']

    # Get one
    get_one_response = client.get(
        f'/api/role_access_controls/{rac_id}'
    )
    assert get_one_response.status == expected_status_codes['read']

    # Update
    update_response = client.patch(
        f'/api/role_access_controls/{rac_id}',
        data=new_data,
    )
    assert update_response.status == expected_status_codes['update']

    if update_response.status == 200:
        data = update_response.json()
        for k in new_data:
            assert new_data[k] == data[k]

    # Delete
    delete_response = client.delete(
        f'/api/role_access_controls/{rac_id}'
    )
    assert delete_response.status == expected_status_codes['delete']

    # Verify delete
    if delete_response.status == 200:
        verify_delete_response = client.get(
            f'/api/role_access_controls/{rac_id}'
        )
        assert verify_delete_response.status == 404
