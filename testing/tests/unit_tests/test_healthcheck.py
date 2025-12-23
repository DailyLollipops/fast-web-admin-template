from playwright.sync_api import APIRequestContext


def test_healthcheck(api_client: APIRequestContext):
    response = api_client.get('/api/docs')
    assert response.status == 200
