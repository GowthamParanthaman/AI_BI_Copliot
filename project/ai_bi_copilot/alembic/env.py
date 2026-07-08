from __future__ import annotations

from logging.config import fileConfig

from alembic import context

from sqlalchemy import (
engine_from_config,
pool,
)

from loguru import logger

from core.config import settings
import database.models

from database.base import Base

print(
    "METADATA TABLES:",
    Base.metadata.tables.keys()
)
target_metadata = Base.metadata



# =====================================================

# IMPORT ALL MODELS

# =====================================================

from database.models.dataset import Dataset

# =====================================================

# ALEMBIC CONFIGURATION

# =====================================================

config = context.config

config.set_main_option(
"sqlalchemy.url",
settings.database_url
)

if config.config_file_name:
    fileConfig(
    config.config_file_name
    )

logger.info(
f"Alembic using database: "
f"{settings.database_url}"
)

# =====================================================

# METADATA REGISTRATION

# =====================================================

target_metadata = Base.metadata

# =====================================================

# OFFLINE MIGRATIONS

# =====================================================

def run_migrations_offline() -> None:
    """
    Run migrations without creating
    a database connection.
    """


    url = config.get_main_option(
        "sqlalchemy.url"
    )

    logger.info(
        "Running offline migrations"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():

        context.run_migrations()


# =====================================================

# ONLINE MIGRATIONS

# =====================================================

def run_migrations_online() -> None:
    """
    Run migrations using
    a live database connection.
    """


    configuration = (
        config.get_section(
            config.config_ini_section
        )
        or {}
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    logger.info(
        "Creating migration connection"
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=(
                settings.DATABASE_TYPE
                == "sqlite"
            ),
        )

        with context.begin_transaction():

            context.run_migrations()

    logger.success(
        "Migration completed"
    )


    # =====================================================

    # ENTRYPOINT

    # =====================================================

    if context.is_offline_mode():


        run_migrations_offline()


    else:


        run_migrations_online()

