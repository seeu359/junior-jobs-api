from api import orm_models as om
from api.base_models import RequestParams, ResponseDone
from api.services import get_queries, get_language, get_compare_type, \
    get_response_done
from datetime import date


class DBStat:

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner) -> om.StatisticsORM:
        return instance.__dict__[self.name]

    def __set__(self, db_instance, value):
        if db_instance.compare_type == 'today':
            db_instance.__dict__[self.name] = db_instance.get_today_stat()
        else:
            db_instance.__dict__[self.name]: list[om.StatisticsORM] = \
                db_instance.get_stat_by_lang()
        db_instance.__dict__[self.name] = db_instance.to_response_model()


class DB:

    stat = DBStat()

    def __init__(
            self,
            params: RequestParams,
    ):
        self.language = get_language(params)
        self.compare_type = get_compare_type(params)
        self.queries = get_queries(params)
        self.stat = None

    def get_stat_by_lang(self) -> list[ResponseDone]:
        with om.session() as s:
            return s.query(om.StatisticsORM).\
                join(om.LanguagesORM). \
                filter(
                om.LanguagesORM.language ==
                self.language).all()

    def get_today_stat(self):
        with om.session() as s:
            return s.query(om.StatisticsORM).\
                join(om.LanguagesORM). \
                filter(
                (om.StatisticsORM.date == date.today()) &
                (om.LanguagesORM.language == self.language)). \
                first()

    def to_response_model(self) -> list[ResponseDone] | ResponseDone:
        if isinstance(self.stat, list):
            for obj in self.stat:
                index = self.stat.index(obj)
                response_obj = get_response_done(
                    obj,
                    self.language,
                    self.compare_type
                )
                self.stat[index] = response_obj._asdict()
            return self.stat
        else:
            response_done = get_response_done(
                self.stat,
                self.language,
                self.compare_type
            )
            return response_done
