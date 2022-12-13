from api import orm_models as om
from api.base_models import RequestParams, Statistics
from api.services import get_queries, get_language, get_compare_type
from datetime import date, timedelta
from loguru import logger


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
        self.stat = Statistics(today=None, ct_stat=None, array_stat=None)
        self._mapper()

    def _mapper(self):
        if self.compare_type == 'today':
            self.get_today_stat()
        elif self.compare_type is None:
            return self.get_array_of_stats()
        else:
            return self.get_ct_stats()

    def get_array_of_stats(self) -> None:
        with om.session() as s:
            request_to_db = s.query(om.StatisticsORM).\
                join(om.LanguagesORM). \
                filter(
                om.LanguagesORM.language ==
                self.language).all()
            self.stat['array_stat'] = request_to_db

    def get_today_stat(self) -> None:
        with om.session() as s:
            request_to_db = s.query(om.StatisticsORM).\
                join(om.LanguagesORM). \
                filter(
                (om.StatisticsORM.date == date.today()) &
                (om.LanguagesORM.language == self.language)).\
                first()
            self.stat['today'] = request_to_db

    def get_ct_stats(self) -> None:
        time_delta = date.today() - timedelta(
            days=TIMEDELTA_DAYS[self.compare_type]
        )
        logger.info(time_delta)
        with om.session() as s:
            self.get_today_stat()
            ct_stat = s.query(om.StatisticsORM).\
                join(om.LanguagesORM).\
                filter(
                (om.StatisticsORM.date == time_delta) &
                (om.LanguagesORM.language == self.language)).first()
            self.stat['ct_stat'] = ct_stat
