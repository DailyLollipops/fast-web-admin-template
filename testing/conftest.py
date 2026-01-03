import os
import random
import shutil
import subprocess
from collections.abc import Callable, Generator
from pathlib import Path

import bcrypt
import httpx
import pytest
from faker import Faker
from playwright.sync_api import APIRequestContext, Playwright
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine, text

from api.database.models.notification import Notification
from api.database.models.user import User
from testing.fixtures import API_URL, BASE_URL, USERS


DATABASE_URL = os.getenv('DATABASE_URL') or ''
BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / 'testing' / 'outputs'
TEMPLATES_DIR = BASE_DIR / 'api' / 'templates' / 'tests'
DATABASE_DIR = BASE_DIR / 'api' / 'database'


@pytest.fixture(scope='session', autouse=True)
def session_setup_and_teardown():
    # Alembic migration
    subprocess.call(['alembic', 'upgrade', 'head'], cwd=DATABASE_DIR)

    # Add initial data (users, etc.)
    url = make_url(DATABASE_URL)
    engine = create_engine(url)
    faker_factory = Faker()
    with engine.connect() as conn:
        with Session(conn) as session:
            # Seed users
            users: list[User] = []
            for role, user in USERS.items():
                new_user = User(
                    name=user['name'],
                    email=user['email'],
                    provider='native',
                    password=bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    role=role,
                    verified=True
                )
                users.append(new_user)
                session.add(new_user)
            session.commit()

            for user in users:
                session.refresh(user)

            # Seed notifications
            for user in users:
                for _ in range(random.randint(3, 5)):
                    notification = Notification(
                        user_id=user.id,
                        triggered_by=user.id,
                        category=random.choice(['info', 'warning', 'error']),
                        title=faker_factory.sentence(),
                        body=faker_factory.sentence(),
                    )
                    session.add(notification)

            session.commit()

    yield

    # Teardown
    db_name = url.database
    url = url.set(database=None)
    engine = create_engine(url)

    with engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS `{db_name}`;'))
        conn.execute(text(f'CREATE DATABASE `{db_name}`;'))

    # Remove generated files
    if TEMPLATES_DIR.exists():
        shutil.rmtree(TEMPLATES_DIR)

    # Artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    logs = [
        '/var/log/supervisor/api.out.log',
        '/var/log/supervisor/api.err.log',
        '/var/log/supervisor/worker.out.log',
        '/var/log/supervisor/worker.err.log',
        '/var/log/supervisor/web.out.log',
        '/var/log/supervisor/web.err.log'
    ]
    for log in logs:
        name = log.split('/')[-1]
        logpath = ARTIFACTS_DIR / name
        shutil.copy(log, logpath)


@pytest.fixture(scope='function')
def db_session():
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
async def auth_header(request):
    '''Logs in user based on param and returns the Authorization header.'''
    user = request.param
    print(f'User: {user}')
    async with httpx.AsyncClient(base_url=API_URL) as client:
        response = await client.post(
            '/auth/login',
            data={'username': user['email'], 'password': user['password']},
        )
        assert response.status_code == 200, f'Login failed for {user['role']}'
        token = response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def api_client(playwright: Playwright) -> Generator[APIRequestContext, None]:
    request_context = playwright.request.new_context(
        base_url=BASE_URL
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def authenticated_api_client(playwright: Playwright) -> Generator[Callable[[str], APIRequestContext], None, None]:
    contexts = []

    def _login(user_key: str):
        user = USERS[user_key]
        context = playwright.request.new_context(base_url=BASE_URL)

        login = context.post(
            '/api/auth/login',
            form={
                'username': user['email'],
                'password': user['password'],
            },
        )

        assert login.ok, f'Login failed for {user_key}: {login.text()}'
        contexts.append(context)

        return context

    yield _login

    for ctx in contexts:
        ctx.dispose()
