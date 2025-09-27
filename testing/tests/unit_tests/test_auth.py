import httpx
import pytest

from testing.fixtures import API_URL


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


@pytest.mark.asyncio
@pytest.mark.parametrize('user', USERS)
async def test_authenticate_user(user):
    async with httpx.AsyncClient(base_url=API_URL) as client:
        # Register
        register_response = await client.post('/auth/register', json=user)
        assert register_response.status_code == 200

        # Login
        login_data = {'username': user['email'], 'password': user['password']}
        login_response = await client.post('/auth/login', data=login_data)
        assert login_response.status_code == 200

        data = login_response.json()
        access_token = data['access_token']
        auth_header = {'Authorization': f'Bearer {access_token}'}

        # Me
        me_response = await client.get('/auth/me', headers=auth_header)
        assert me_response.status_code == 200

        # Generate API key
        generate_api_response = await client.post('/auth/generate_api_key', headers=auth_header)
        assert generate_api_response.status_code == 200



@pytest.mark.asyncio
@pytest.mark.parametrize('user', USERS)
async def test_login_wrong_password(user):
    async with httpx.AsyncClient(base_url=API_URL) as client:
        login_data = {'username': user['email'], 'password': 'wrongpass'}
        login_response = await client.post('/auth/login', data=login_data)
        assert login_response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_email():
    async with httpx.AsyncClient(base_url=API_URL) as client:
        login_data = {'username': 'doesnotexist@example.com', 'password': 'password'}
        login_response = await client.post('/auth/login', data=login_data)
        assert login_response.status_code == 401
