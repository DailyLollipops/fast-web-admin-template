import pytest
from playwright.sync_api import Page, expect

from testing.fixtures import USERS, WEB_URL


@pytest.mark.parametrize('user', USERS)
def test_correct_credentials(page: Page, user):
    page.goto(f'{WEB_URL}/#/login/')

    expect(page.locator('#email')).to_be_visible()
    expect(page.locator('#password')).to_be_visible()
    expect(page.locator('#login')).to_be_visible()

    page.fill('#email', USERS[user]['email'])
    page.fill('#password', USERS[user]['password'])
    page.click('#login')

    expect(page.locator('#react-admin-title')).to_have_text('Dashboard')


@pytest.mark.parametrize('user', USERS)
def test_incorrect_email(page: Page, user):
    page.goto(f'{WEB_URL}/#/login/')

    expect(page.locator('#email')).to_be_visible()
    expect(page.locator('#password')).to_be_visible()
    expect(page.locator('#login')).to_be_visible()

    page.fill('#email', 'invalid@example.com')
    page.fill('#password', USERS[user]['password'])
    page.click('#login')

    expect(page).to_have_url(f'{WEB_URL}/#/login')


@pytest.mark.parametrize('user', USERS)
def test_incorrect_password(page: Page, user):
    page.goto(f'{WEB_URL}/#/login/')

    expect(page.locator('#email')).to_be_visible()
    expect(page.locator('#password')).to_be_visible()
    expect(page.locator('#login')).to_be_visible()

    page.fill('#email', USERS[user]['email'])
    page.fill('#password', 'invalidpassword')
    page.click('#login')

    expect(page).to_have_url(f'{WEB_URL}/#/login')
