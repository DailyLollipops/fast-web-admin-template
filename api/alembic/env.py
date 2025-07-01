import os
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Import your models to ensure they are registered with SQLAlchemy
from models import *

# This is the configuration object used by Alembic to generate the migrations
config = context.config

# Replace the placeholder with the actual environment variable value
sqlalchemy_url = os.getenv('DATABASE_URL')
config.set_main_option('sqlalchemy.url', sqlalchemy_url)

# Interpret the config file for Python logging.
from logging.config import fileConfig
fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    connection = engine.connect()
    context.configure(
        connection=connection, target_metadata=target_metadata
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
