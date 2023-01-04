from datetime import date, timedelta

from loguru import logger
from sqlalchemy.sql.expression import func

from api.lib import orm_models as om
from api.lib.base_models import RequestParams, Statistics
from api.lib.services import get_compare_type, get_language, get_queries


class DB:

    LANGUAGES_ID = {
        'python': 1,
        'php': 2,
        'javascript': 3,
        'ruby': 4,
        'java': 5,
    }

    TIMEDELTA_DAYS = {
        'week': 7,
        'month': 30,
    }

    __slots__ = (
        'language',
        'compare_type',
        'queries',
        'stat',
    )

    def __init__(
            self,
            params: RequestParams
    ):
        self.language = get_language(params)
        self.compare_type = get_compare_type(params)
        logger.info(self.compare_type)
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
            return self.get_today_stat()

        if self.compare_type == 'custom':
            return self.get_custom_stats()

        if self.compare_type is None:
            return self.get_array_of_stats()

        else:
            return self.get_ct_stats()

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
            days=self.TIMEDELTA_DAYS[self.compare_type]
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

    def upload_statistics(self, data: dict[str, tuple[int, int]]) -> None:
        with om.session() as s:
            for lang, vacs in data.items():

                max_id = s.query(func.max(om.StatisticsORM.id)).first()[0]

                record = om.StatisticsORM(
                    id=max_id + 1,
                    language_id=self.LANGUAGES_ID[lang],
                    region_id=113,
                    site_id=1,
                    vacancies=vacs[0],
                    date=date.today(),
                    no_experience=vacs[1]
                )
                s.add(record)

            s.commit()
