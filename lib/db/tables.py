import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime 
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class Situation(Base):

    __tablename__ = 'emotion'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    situation = Column(String)
    mind = Column(String)
    emotion = Column(String)
    body = Column(String)
    replacement = Column(String)
    create_time = Column(DateTime)

    def __repr__(self) -> str:
        text = f"""Situation:
    {self.situation}
minds:
    {self.mind}
emotions:
    {self.emotion}
body feelings:
    {self.body}
replacement:
    {self.replacement}"""

        return text


# def get_engine(postgre_password: str, postgre_port:str, postgre_host:str):
#     url = f'postgresql+psycopg2://postgres:{postgre_password}@{postgre_host}:{postgre_port}/emotion_bot'
#     engine = create_engine(url)
#     return engine


def get_engine():
    url = f"sqlite:///data/main.db"
    engine = create_engine(url)
    return engine


def create_data_base_and_tables(engine):

    if not database_exists(engine.url):
        create_database(engine.url)
        logger.info(f"database was created, url={engine.url}")
    Base.metadata.create_all(engine)

