from api import orm_models
from datetime import date


class DBStat:

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner) -> orm_models.StatisticsORM:
        return instance.__dict__[self.name]

    def __set__(self, db_instance, value):
        if db_instance.compare_type == 'today':
            db_instance.__dict__[self.name] = db_instance.get_today_stat()
        else:
            db_instance.__dict__[self.name] = \
                db_instance.get_stat_by_lang()


class DB:

    stat = DBStat()

    def __init__(
            self,
            language: str,
            compare_type: str | None = None,
            **queries: str
    ):
        self.language = language
        self.compare_type = compare_type
        self.queries = dict(**queries)
        self.stat = None

    def get_stat_by_lang(self):
        with orm_models.session() as s:
            return s.query(orm_models.StatisticsORM). \
                        join(orm_models.LanguagesORM). \
                        filter(
                        orm_models.LanguagesORM.language ==
                        self.language).all()

    def get_today_stat(self):
        with orm_models.session() as s:
            return s.query(orm_models.StatisticsORM).\
                join(orm_models.LanguagesORM). \
                filter(
                (orm_models.StatisticsORM.date == date.today()) &
                (orm_models.LanguagesORM.language == self.language)). \
                first()