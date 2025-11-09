from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..settings.config import config


engine = create_engine(url=config.DB_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    try:
        session = sessionLocal()
        yield session
    finally:
        session.close()
