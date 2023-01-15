from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from api.settings import DATABASE

engine = create_engine(DATABASE, future=True)

Session = sessionmaker(engine, autoflush=False, autocommit=False)

Base = declarative_base(engine)


def get_session() -> Session:

    session = Session()
    try:
        yield session
    finally:
        session.close()
