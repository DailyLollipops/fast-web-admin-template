import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv('DATABASE_URL') or ''
BASE_DIR = Path(__file__).resolve().parent
ALEMBIC_DIR = BASE_DIR.parent / 'api' / 'database' / 'alembic'
ALEMBIC_INI_PATH = BASE_DIR.parent / 'api' / 'database' / 'alembic.ini'


@pytest.fixture(scope='session', autouse=True)
def initialize_environment():
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL)
    alembic_cfg.set_main_option('script_location', str(ALEMBIC_DIR))
    command.upgrade(alembic_cfg, 'head')

    yield

    from sqlalchemy.engine import make_url
    url = make_url(DATABASE_URL)

    db_name = url.database
    url = url.set(database=None)
    engine = create_engine(url)

    with engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS `{db_name}`;'))
        conn.execute(text(f'CREATE DATABASE `{db_name}`;'))


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
