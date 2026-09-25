# Import Python's asyncio module so Alembic can execute the asynchronous
# SQLAlchemy engine from its normally synchronous command-line entry point.
import asyncio

# Import Alembic's logging helper. It reads the logging sections in
# alembic.ini and configures Python's logging system.
from logging.config import fileConfig

# Import SQLAlchemy's pool module so the migration engine can use NullPool.
# NullPool avoids retaining a connection pool after a one-shot migration.
from sqlalchemy import pool

# Import the helper that builds an AsyncEngine from prefixed configuration
# values, such as the "sqlalchemy.url" value below.
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import Alembic's runtime context. It reads command-line options and executes
# the migration operations for the requested revision range.
from alembic import context

# Import the application's settings so Alembic uses the same database URL as
# the application, including the selected .env.* file.
from app.config_settings.settings import settings

# Import the application's declarative base. Base.metadata contains the schema
# definitions that Alembic uses during autogeneration.
from app.db.database import Base

# Import all model modules exposed by app.models. This registers User and Todo
# in Base.metadata before target_metadata is assigned below.
from app.models import *

# Get Alembic's Config object for the current command. It represents
# alembic.ini plus any command-line configuration supplied to Alembic.
config = context.config


# Load the logger definitions from alembic.ini when a config file is present.
# This enables Alembic and SQLAlchemy messages such as migration progress logs.
if config.config_file_name is not None:
    # Apply the [loggers], [handlers], and [formatters] sections from the file.
    fileConfig(config.config_file_name)


# Tell Alembic which SQLAlchemy metadata describes the desired application
# schema. Autogenerate compares this metadata with the live database schema.
target_metadata = Base.metadata


# Generate migration SQL without opening a live database connection.
def run_migrations_offline() -> None:
    # Configure the migration context using only a database URL.
    context.configure(
        # Use the application's URL instead of alembic.ini's placeholder URL.
        url=settings.DATABASE_URL,
        # Give Alembic the model metadata used for schema comparison.
        target_metadata=target_metadata,
        # Render literal values directly in generated SQL.
        literal_binds=True,
        # Use named bind parameters when the dialect renders parameters.
        dialect_opts={"paramstyle": "named"},
    )

    # Start Alembic's transaction context. Offline mode renders transaction
    # statements such as BEGIN and COMMIT for transactional DDL dialects.
    with context.begin_transaction():
        # Execute the migration functions for the requested revision range.
        context.run_migrations()


# Run migration operations through a synchronous SQLAlchemy Connection.
# SQLAlchemy's AsyncConnection.run_sync() calls this function below.
def do_run_migration(connection):
    # Bind Alembic to the supplied connection and expose the model metadata.
    context.configure(connection=connection, target_metadata=target_metadata)

    # Begin the transaction containing this migration run.
    with context.begin_transaction():
        # Execute the requested upgrade or downgrade operations.
        context.run_migrations()


# Create an async engine and execute the migration against PostgreSQL.
async def run_async_migration():
    # Build an AsyncEngine from a configuration mapping. The key below starts
    # with "sqlalchemy." so it is selected by prefix="sqlalchemy.".
    connectable = async_engine_from_config(
        {
            # Supply the same async URL used by the application, typically
            # postgresql+asyncpg://username:password@host/database.
            "sqlalchemy.url": settings.DATABASE_URL
        },
        # Read configuration keys beginning with this prefix.
        prefix="sqlalchemy.",
        # Do not retain pooled connections after the migration command ends.
        poolclass=pool.NullPool,
    )

    # Open one async connection. The context manager closes it automatically.
    async with connectable.connect() as conection:
        # Alembic's migration context is synchronous, so run it through the
        # synchronous facade supplied by SQLAlchemy's async connection.
        await conection.run_sync(do_run_migration)


# Select the normal live-database migration path.
def run_migrations_online() -> None:
    # Alembic calls this function synchronously, so start an asyncio event loop
    # and wait until the asynchronous migration has completed.
    asyncio.run(run_async_migration())


# Alembic sets offline mode for commands such as `upgrade head --sql`.
if context.is_offline_mode():
    # Produce SQL text without connecting to PostgreSQL.
    run_migrations_offline()
else:
    # Connect to PostgreSQL and execute the migration operations.
    run_migrations_online()
