from logging.config import fileConfig

from dotenv import load_dotenv
from isort import settings
from sqlalchemy import engine_from_config
from sqlalchemy import pool


from alembic import context
from logging.config import fileConfig
import sys
import os

# вот без этого from DataBase.Database import Base отказывается работать
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataBase.Database import Base
from DataBase.Shemas import TodooDB  # noqa

load_dotenv()

# Async PostgreSQL URL (ВАЖНО: postgresql+asyncpg://)
POSTGRES_URL = os.getenv("POSTGRES_URL")
config = context.config

config.set_main_option(
    "sqlalchemy.url",
    "postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase?async_fallback=True",
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
