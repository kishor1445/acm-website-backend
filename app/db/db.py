from sqlmodel import SQLModel, Session
from app.config import db_engine
from . import models  # Sets the metadata for the create_table() to create tables


def create_table(engine):
    """
    Creates all the tables by using the meta of the SQLModel class
    """
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(db_engine) as session:
        yield session
