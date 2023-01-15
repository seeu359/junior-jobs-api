import datetime

from fastapi import Depends, HTTPException, status
import requests
from sqlalchemy import func

from api.database import get_session, Session
from api.stat import schemes, models

RUSSIA_ID = 113


class StatServices:

    LANGUAGES_ID = {
        'python': 1,
        'php': 2,
        'javascript': 3,
        'ruby': 4,
        'java': 5,
    }
    TODAY = datetime.date.today()
    COEFFICIENT = 100

    @classmethod
    def exception(cls, status_code: int, detail: str):

        raise HTTPException(status_code=status_code, detail=detail)

    @classmethod
    def get_data_from_hh_api(cls) -> dict[str, tuple[int, int]]:
        """
        Request to HH API to get data about vacancies.
        :return: dict with tuple where tuple[0] - all vacancies count,
        tuple[1] - no experience required vacancies count.
        """

        languages = ['python', 'php', 'javascript', 'ruby', 'java']
        result = dict()

        for lang in languages:
            all_vacs_template = 'https://api.hh.ru/vacancies?' \
                                'text={}+junior&per_page=100&area={}'. \
                format(lang, RUSSIA_ID)

            no_exp_template = 'https://api.hh.ru/vacancies?' \
                              'text={}+junior&per_page=100&' \
                              'area=${}&experience=noExperience'. \
                format(lang, RUSSIA_ID)

            all_vacs = \
                requests.get(all_vacs_template).json()

            no_exp_vacs = requests.get(no_exp_template).json()

            result[lang] = all_vacs['found'], no_exp_vacs['found']
        return result

    def check_data_in_db(self):
        data = self.session.query(models.StatisticsORM). \
            filter(
            models.StatisticsORM.date == self.TODAY).first()

        if data is not None:
            self.exception(
                status.HTTP_409_CONFLICT,
                'The data has already been uploaded today'
            )

    def get_stat_from_db(
            self, language: str, time_delta: datetime.date
    ) -> models.StatisticsORM:

        return self.session.query(models.StatisticsORM). \
            join(models.LanguagesORM). \
            filter(
            (models.StatisticsORM.date == time_delta) &
            (models.LanguagesORM.language == language)). \
            first()

    @classmethod
    def get_statistics_schemes(
            cls, language, compare_type, vacs_were, vacs_became, stats,
    ) -> schemes.CTStatistics:

        return schemes.CTStatistics(
            language=language,
            compare_type=compare_type,
            vacs_were=vacs_were,
            vacs_became=vacs_became,
            comparison=stats,
        )

    def __init__(self, session: Session = Depends(get_session)):

        self.session = session

    def compute_stat(
            self, reduced: models.StatisticsORM, reducer: models.StatisticsORM
    ) -> dict[str, int]:
        in_amount = reduced.vacancies - reducer.vacancies

        in_percents = round(reduced.vacancies / reducer.vacancies *
                            self.COEFFICIENT - self.COEFFICIENT)

        return {
            'in_amount': in_amount,
            'in_percent': in_percents,
        }

    def get_today_stat(self, language: str) -> schemes.Statistics:

        today = self.get_stat_from_db(language, self.TODAY)

        if not today:

            self.exception(
                status.HTTP_404_NOT_FOUND, 'The data has not yet been uploaded'
            )

        return schemes.Statistics(
            language=language,
            date=today.date,
            vacancies=today.vacancies,
            no_experience=today.no_experience,
            region=today.region_id,
            site=today.site_id,
            compare_type='today',
        )

    def get_stat_by_compare_type(
            self, language: str, compare_data: tuple
    ) -> schemes.CTStatistics:

        days = compare_data[0]
        compare_type = compare_data[1]

        # It's plug since the data for 3 or more months have not
        # yet been collected
        if days != 7 or days != 30:
            days = 30
        #
        time_delta = self.TODAY - datetime.timedelta(days=days)

        today = self.get_stat_from_db(language, self.TODAY)
        week = self.get_stat_from_db(language, time_delta)

        calculated_stats = self.compute_stat(today, week)

        return self.get_statistics_schemes(
            language,
            compare_type,
            week.vacancies,
            today.vacancies,
            calculated_stats
        )

    def get_array_stat(self, language: str) -> list[schemes.Statistics]:

        stats = self.session.query(models.StatisticsORM). \
            join(models.LanguagesORM). \
            filter(
            models.LanguagesORM.language ==
            language).all()

        return [schemes.Statistics(
            language=language,
            date=_.date,
            vacancies=_.vacancies,
            no_experience=_.no_experience,
            region=_.region_id,
            site=_.site_id,
            compare_type='null'
        ) for _ in stats]

    def upload(self) -> list:

        self.check_data_in_db()

        data = self.get_data_from_hh_api()
        for lang, vacs in data.items():

            max_id = self.session.query(
                func.max(
                    models.StatisticsORM.id
                )
            ).first()[0]

            record = models.StatisticsORM(
                id=max_id + 1,
                language_id=self.LANGUAGES_ID[lang],
                region_id=113,
                site_id=1,
                vacancies=vacs[0],
                date=self.TODAY,
                no_experience=vacs[1]
            )
            self.session.add(record)

        self.session.commit()

        return list()
