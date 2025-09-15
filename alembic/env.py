from __future__ import annotations

import os

from logging.config import fileConfig

from alembic import context

from sqlalchemy import create_engine, pool

from app.models import Base  # your SQLAlchemy 2.0 typed models


config = context.config

if config.config_file_name:

    fileConfig(config.config_file_name)


target_metadata = Base.metadata

DATABASE_URL = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def run_migrations_offline():

    context.configure(

        url=DATABASE_URL,

        target_metadata=target_metadata,

        literal_binds=True,

        compare_type=True,

        compare_server_default=True,

    )

    with context.begin_transaction():

        context.run_migrations()


def run_migrations_online():

    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:

        context.configure(

            connection=connection,

            target_metadata=target_metadata,

            compare_type=True,

            compare_server_default=True,

        )

        with context.begin_transaction():

            context.run_migrations()


if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()

