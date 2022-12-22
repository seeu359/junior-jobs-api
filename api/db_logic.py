from api import orm_models as om
from api.base_models import RequestParams, Statistics
from api.services import get_queries, get_language, get_compare_type
from datetime import date, timedelta


TIMEDELTA_DAYS = {
    'week': 7,
    'month': 30,
}


class DB:

    def __init__(
            self,
            params: RequestParams
    ):
        self.language = get_language(params)
        self.compare_type = get_compare_type(params)
        self.queries = get_queries(params)
        self.stat = Statistics(
            today=None,
            ct_stat=None,
            array_stat=None,
            custom_stat={
                'date1': None,
                'date2': None,
            },
        )
        self._mapper()

    def _mapper(self):
        if self.compare_type == 'today':
            self.get_today_stat()
        elif self.compare_type == 'custom':
            self.get_custom_stats()
        elif self.compare_type is None:
            self.get_array_of_stats()
        else:
            self.get_ct_stats()

    def get_array_of_stats(self) -> None:
        with om.session() as s:
            list_stats = s.query(om.StatisticsORM).\
                join(om.LanguagesORM). \
                filter(
                om.LanguagesORM.language ==
                self.language).all()
            self.stat['array_stat'] = list_stats

    def get_today_stat(self) -> None:
        with om.session() as s:
            today_stat = s.query(om.StatisticsORM).\
                join(om.LanguagesORM). \
                filter(
                (om.StatisticsORM.date == date.today()) &
                (om.LanguagesORM.language == self.language)).\
                first()
            self.stat['today'] = today_stat

    def get_ct_stats(self) -> None:
        time_delta = date.today() - timedelta(
            days=TIMEDELTA_DAYS[self.compare_type]
        )
        with om.session() as s:
            self.get_today_stat()
            ct_stat = s.query(om.StatisticsORM).\
                join(om.LanguagesORM).\
                filter(
                (om.StatisticsORM.date == time_delta) &
                (om.LanguagesORM.language == self.language)).first()
            self.stat['ct_stat'] = ct_stat

    def get_custom_stats(self):
        with om.session() as s:
            date1 = s.query(om.StatisticsORM).\
                join(om.LanguagesORM).\
                filter(
                (om.StatisticsORM.date == self.queries['date1']) &
                (om.LanguagesORM.language == self.language)).first()
            date2 = s.query(om.StatisticsORM).\
                join(om.LanguagesORM).\
                filter(
                (om.StatisticsORM.date == self.queries['date2']) &
                (om.LanguagesORM.language == self.language)).first()
            self.stat['custom_stat']['date1'] = date1
            self.stat['custom_stat']['date2'] = date2
