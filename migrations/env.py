import sys
import os
from logging.config import fileConfig
from alembic import context
from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from api.utils.database import engine
from api.model import auth_model

target_metadata = SQLModel.metadata

def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
