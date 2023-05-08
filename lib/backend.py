import sqlalchemy.engine
from sqlalchemy import create_engine, insert, func
from sqlalchemy.orm import scoped_session, Session
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass
from typing import Any
from datetime import datetime
import logging

from lib.db.tables import Situation
from configs.definitions import ROOT_DIR

logger = logging.getLogger(__name__)


@dataclass
class Response:
    """every backend method should return response object"""
    status: int  # 0 status - everything is good, else - there is error
    answer: Any  # result


def db_executor(func):
    """create and close sqlalchemy session for class methods which execute sql statement"""
    def inner(*args, **kwargs):
        self_ = args[0]

        with Session(self_.engine) as session:
            func(*args, **kwargs, session=session)
            session.commit()
    return inner


def db_selector(func):
    """create and close sqlalchemy session for class methods which return query result"""
    def inner(*args, **kwargs):
        self_ = args[0]

        with Session(self_.engine) as session:
            result = func(*args, **kwargs, session=session)
            return result
    return inner


class TableProcessor:

    def __init__(self, engine):
        session_factory = sessionmaker(bind=engine)
        self.engine = engine
        self.Session = scoped_session(session_factory)

    @db_selector
    def get_query_result(self, query: "sqlalchemy.orm.query.Query", session=None) -> list["table_model"]:
        result = session.execute(query).scalars().all()
        return result

    @db_executor
    def _insert_values(self, table_model: "sqlalchemy.orm.decl_api.DeclarativeMeta", data: dict, session=None) -> None:
        ins_command = insert(table_model).values(**data)
        session.execute(ins_command)

    @db_selector
    def _get_all_data(self, table_model: "sqlalchemy.orm.decl_api.DeclarativeMeta", session=None) -> list['table_model']:
        query = session.query(table_model)
        result = self.get_query_result(query)
        return result

    @db_selector
    def _get_filtered_data(self, table_model, filter_values: dict, session=None) -> list['table_model']:
        query = session.query(table_model)
        for filter_column in filter_values:
            query = query.filter(getattr(table_model, filter_column) == filter_values[filter_column])
        result = self.get_query_result(query)
        return result

    @db_executor
    def _change_column_value(self, table_model, filter_values: dict, change_values: dict, session=None) -> None:
        query = session.query(table_model)
        for filter_column in filter_values:
            query = query.filter(getattr(table_model, filter_column) == filter_values[filter_column])
        query.update(change_values)

    @db_selector
    def _get_max_value_of_column(self, table_model, column: str, session=None):

        query = func.max(getattr(table_model, column))
        result = self.get_query_result(query)[0]

        # case with empty table
        if not result:
            result = 0

        return result


class SituationProcessor(TableProcessor):

    def __init__(self, engine):
        super().__init__(engine)
        self.table_model = Situation

    def get_max_id(self):
        return self._get_max_value_of_column(self.table_model, 'id')

    def insert_emotion(self,
                       telegram_id: int,
                       situation: str,
                       mind: str,
                       emotion: str,
                       body: str,
                       replacement: str,
                       create_time: datetime
                       ) -> int:

        try:
            current_id = self.get_max_id() + 1
            data = {
                'id': current_id,
                'telegram_id': telegram_id,
                'situation': situation,
                'mind': mind,
                'emotion': emotion,
                'body': body,
                'replacement': replacement,
                'create_time': create_time
            }
            self._insert_values(self.table_model, data)
            logger.info(f"situation '{situation}' was inserted to DB")
            return Response(0, current_id)
        except Exception as e:
            logger.error(f"situation '{situation}' was not inserted to DB, exception - {e}")
            return Response(1, e)

    def get_last_n_situations(self, telegram_id: int, n: int) -> list[Situation]:
        filter_values = {
            'telegram_id': telegram_id
        }
        try:
            situations = self._get_filtered_data(self.table_model, filter_values)
            situations = sorted(situations, key=lambda x: x.create_time, reverse=True)[:n][::-1]
            logger.info(f"last {n} situations was passed")
            return Response(0, situations)
        except Exception as e:
            logger.error(f"all active situations was not passed, exception - {e}")
            return Response(1, e)


class Backend:

    def __init__(self, engine: sqlalchemy.engine.base.Engine):
        self.situation_processor = SituationProcessor(engine)

    def add_situation(self,
                       telegram_id: int,
                       situation: str,
                       mind: str,
                       emotion: str,
                       body: str,
                       replacement: str,
                       create_time: datetime) -> Response:
        return self.situation_processor.insert_emotion(telegram_id, situation, mind,
                                                       emotion, body, replacement, create_time)

    def get_last_n_situations(self, telegram_id: int, n: int):
        return self.situation_processor.get_last_n_situations(telegram_id, n)
