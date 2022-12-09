from fastapi import status
from pydantic import ValidationError
from typing import Union
from api.db_logic import DB
from api.orm_models import StatisticsORM
from api.base_models import ResponseDone, ResponseError, PathParts


StatusCode = int


def get_request_data(language, compare_type=None, **queries):
    """Abstraction for handling requests path parts and request queries
    and return them in dict(or specially class?)"""
    params = dict(
        language=language,
        compare_type=compare_type,
        **queries
    )
    return params


def get_processed_data(data: dict) -> \
        tuple[Union[ResponseDone, list[ResponseDone], ResponseError],
              StatusCode]:
    try:
        data = PathParts(
            language=data['language'],
            compare_type=data['compare_type'],
        )
    except ValidationError:
        return \
            _get_error_data(
                data['language'],
                data['compare_type']), status.HTTP_200_OK

    if not data.compare_type:
        data_from_db = _get_list_data_by_language(data.language)
        return data_from_db, status.HTTP_404_NOT_FOUND

    elif data.compare_type == 'today':
        data_from_db = DB(data.language, data.compare_type).stat
        return _get_response_data(
            data_from_db,
            data.language,
            data.compare_type), status.HTTP_200_OK


def _get_list_data_by_language(
        language: str
) -> list[ResponseDone]:

    data: list[StatisticsORM] = DB(language).stat
    statistics = list()
    for record in data:
        statistics.append(_get_response_data(record, language))
    return statistics


def _get_response_data(
        data: StatisticsORM,
        language: str,
        compare_type: str | None = None,
) -> ResponseDone:

    """Create pydantic BaseModel with responses data.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""

    return ResponseDone(
        language=language,
        date=str(data.date),
        vacancies=data.vacancies,
        no_experience=data.no_experience,
        region=data.region_id,
        site=data.site_id,
        compare_type=compare_type,
    )


def _get_error_data(
        language: str,
        compare_type: str,
) -> ResponseError:

    """Create pydantic BaseModel of error.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""

    return ResponseError(
        errors={
            'type': 'not_found',  # Plug
            'count': 1
        },
        language=language,
        compare_type=compare_type,
        query=None,
    )
