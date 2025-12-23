import pytest
from playwright.sync_api import APIRequestContext


USERS = [
    {
        'name': 'John Smith',
        'email': 'johnsmith@gmail.com',
        'password': 'password',
        'confirm_password': 'password',
    },
    {
        'name': 'Jane Doe',
        'email': 'janedoe@gmail.com',
        'password': 'password123',
        'confirm_password': 'password123',
    },
    {
        'name': 'Alice Johnson',
        'email': 'alice@gmail.com',
        'password': 'alicepass',
        'confirm_password': 'alicepass',
    },
]


@pytest.mark.parametrize('user', USERS)
def test_authenticate_user(api_client: APIRequestContext, user):
    # Register
    register_response = api_client.post('/api/auth/register', data=user)
    assert register_response.status == 200

    # Login
    login_data = {'username': user['email'], 'password': user['password']}
    login_response = api_client.post('/api/auth/login', form=login_data)
    assert login_response.status == 200

    # Me
    me_response = api_client.get('/api/auth/me')
    assert me_response.status == 200

    # Generate API key
    generate_api_response = api_client.post('/api/auth/generate_api_key')
    assert generate_api_response.status == 200


@pytest.mark.parametrize('user', USERS)
def test_login_wrong_password(api_client: APIRequestContext, user):
    login_data = {'username': user['email'], 'password': 'wrongpass'}
    login_response = api_client.post('/api/auth/login', form=login_data)
    assert login_response.status == 401


def test_login_wrong_email(api_client: APIRequestContext):
    login_data = {'username': 'doesnotexist@example.com', 'password': 'password'}
    login_response = api_client.post('/api/auth/login', form=login_data) # type: ignore
    assert login_response.status == 401
