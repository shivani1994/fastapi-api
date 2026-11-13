import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(db_url)
DBSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

