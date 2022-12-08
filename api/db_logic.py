import datetime
from api import models
from pydantic import BaseModel, ValidationError
from typing import Literal
from datetime import date


class Languages(BaseModel):
    languages: Literal['python', 'java', 'javascript', 'php', 'ruby']


class ResponseData(BaseModel):
    language: Languages
    date: datetime.date
    vacancies: int
    no_experience: int
    region: int
    site: int
    compare_type: str | None


def _get_response_data(
        data: models.StatisticsORM,
        language,
        compare_type
) -> ResponseData:
    response = ResponseData(
        language=language,
        date=data.date,
        vacancies=data.vacancies,
        no_experience=data.no_experience,
        region=data.region_id,
        site=data.site_id,
        compare_type=compare_type,
    )
    return response


def get_processed_data(data: dict) -> ResponseData | dict:
    try:
        language, compare_type = parse_request_data(data)
    except ValidationError:
        return {'data': None}
    if not compare_type:
        pass
    elif compare_type == 'today':
        data_from_db = _get_today_stat(language.languages)
        response_data = _get_response_data(data_from_db, language,
                                           compare_type)
        return response_data


def parse_request_data(data: dict[str, str]) -> tuple[Languages, str]:
    language = Languages(languages=data['language'])
    compare_type = data['compare_type']
    return language, compare_type


# Make easiest request to db - request to get today data 
def _get_today_stat(language: str):
    with models.session() as s:
        data = s.query(models.StatisticsORM).\
            join(models.LanguagesORM).\
            filter(
                       (models.StatisticsORM.date == date.today()) &
                       (models.LanguagesORM.language == language)).first()
        return data


def _get_data_by_language():
    pass


print(get_processed_data({'language': 'pyhon', 'compare_type': 'today'}))
