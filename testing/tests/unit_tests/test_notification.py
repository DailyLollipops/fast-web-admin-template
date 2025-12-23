import random

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
            'read': 200,
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
def test_notification_crud(
    authenticated_api_client,
    user_key: str,
    expected_status_codes: dict[str, int],
):
    """
    Test notification CRUD workflow per user role.
    """
    client: APIRequestContext = authenticated_api_client(user_key)
    faker = Faker()

    original_data = {
        'user_id': 3,
        'category': 'info',
        'title': faker.sentence(),
        'body': faker.sentence(),
    }

    new_data = {
        'category': 'info',
        'title': faker.sentence(),
        'body': faker.sentence(),
    }

    # Create
    create_response = client.post(
        '/api/notifications',
        data=original_data,
    )

    assert create_response.status == expected_status_codes['create']

    if create_response.status == 200:
        data = create_response.json()
        notification_id = data['id']

        for k in original_data:
            assert original_data[k] == data[k]

    # Get list
    get_list_response = client.get('/api/notifications')
    assert get_list_response.status == expected_status_codes['read']

    notification_ids = [
        d['id'] for d in get_list_response.json().get('data', [])
    ]
    assert len(notification_ids) > 0

    notification_id = notification_ids[0]

    # Get one
    get_one_response = client.get(
        f'/api/notifications/{notification_id}'
    )
    assert get_one_response.status == expected_status_codes['read']

    # Update
    update_response = client.patch(
        f'/api/notifications/{notification_id}',
        data=new_data,
    )

    assert update_response.status == expected_status_codes['update']

    if update_response.status == 200:
        data = update_response.json()
        for k in new_data:
            assert new_data[k] == data[k]

    # Delete
    delete_response = client.delete(
        f'/api/notifications/{notification_id}'
    )

    assert delete_response.status == expected_status_codes['delete']

    # Verify delete
    if delete_response.status == 200:
        verify_delete_response = client.get(
            f'/api/notifications/{notification_id}'
        )
        assert verify_delete_response.status == 404


@pytest.mark.parametrize(
    'user_key',
    USERS.keys(),
)
def test_notification_not_owner(
    authenticated_api_client,
    user_key: str,
):
    """
    Verify a user cannot access another user's notifications.
    """
    client: APIRequestContext = authenticated_api_client(user_key)

    get_list_response = client.get('/api/notifications')
    assert get_list_response.status == 200

    notification_ids = [
        d['id'] for d in get_list_response.json().get('data', [])
    ]
    assert len(notification_ids) > 0

    random_ids = set(range(1, 2000)) - set(notification_ids)

    for _ in range(10):
        random_id = random.choice(list(random_ids))

        get_one_response = client.get(
            f'/api/notifications/{random_id}'
        )
        assert get_one_response.status == 404
