from sqlmodel import create_engine, Session
from app.db.db import create_table, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///acm-test.db"

db_engine = create_engine(TEST_DATABASE_URL)

create_table(db_engine)


def _get_db():
    with Session(db_engine) as db:
        yield db


app.dependency_overrides[get_db] = _get_db
