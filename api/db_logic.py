from api import orm_models
from datetime import date


class DBStat:

    def __init__(self, request_to_db=None):
        self.request_to_db = request_to_db

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner) -> orm_models.StatisticsORM:
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        with orm_models.session() as s:
            if instance.compare_type:
                instance.__dict__[self.name] = \
                    s.query(orm_models.StatisticsORM).\
                    join(orm_models.LanguagesORM).\
                    filter(
                    (orm_models.StatisticsORM.date == date.today()) &
                    (orm_models.LanguagesORM.language == instance.language)).\
                    first()
            else:
                instance.__dict__[self.name] = instance.stat_request()


class DB:

    stat = DBStat()

    def __init__(
            self, language: str,
            compare_type: str | None = None,
            **queries: str
    ):
        self.language = language
        self.compare_type = compare_type
        self.queries = dict(**queries)
        self.stat = None

    def stat_request(self):
        with orm_models.session() as s:
            return s.query(orm_models.StatisticsORM). \
                        join(orm_models.LanguagesORM). \
                        filter(
                        orm_models.LanguagesORM.language ==
                        self.language).all()
