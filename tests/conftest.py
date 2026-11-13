import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# The application database module requires a URL when imported. Tests use an
# in-memory SQLite database and replace the engine below before importing app.
os.environ["DATABASE_URL"] = "sqlite://"

import database
import db_models


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autoflush=False, autocommit=False, bind=test_engine)

# Use an in-memory database for tests. Replace the application database before
# importing the app so its routes use the test engine.
database.engine = test_engine
database.DBSession = TestSession
db_models.Base.metadata.create_all(bind=test_engine)

from main import app  # noqa: E402


@pytest.fixture
def clean_database():
    with TestSession() as db:
        db.query(db_models.Product).delete()
        db.commit()


@pytest.fixture
def db_session():
    with TestSession() as db:
        db.query(db_models.Product).delete()
        db.commit()
        yield db
