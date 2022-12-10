from fastapi import status
from pydantic import ValidationError
from typing import Union
from api.db_logic import DB
from api.orm_models import StatisticsORM
from api.base_models import ResponseDone, ResponseError, RequestParams


StatusCode = int


def get_language(params: RequestParams) -> str:
    """
    Selector for receive language from RequestParams
    :param params: type(RequestParams)
    :return: str
    """
    return params.language


def get_compare_type(params: RequestParams) -> str:
    """
    Selector for receive compare_type from RequestParams
    :param params: RequestParams
    :return: str
    """
    return params.compare_type


def get_queries(params: RequestParams) -> dict:
    """
    Selector for receive queries from RequestParams
    :param params: RequestParams
    :return: str
    """
    return {
        'param1': params.param1,
        'param2': params.param2,
    }


def make_request_params(
        language: str,
        *,
        construct: bool = False,
        compare_type: str | None = None,
        **queries: str | None,
        ) -> RequestParams:
    """
    Constructor for request params. Make RequestParams pydantic BaseModel
    class, which contains all params of user request. If construct
    param is True, error validation does not happen, else - params
    will be validated. All users params must be constructed by this
    abstraction!
    :param language: The only one require param. It has in all requests to API.
    :param construct: type(bool). If True validation does not happen.
    :param compare_type: Optional param. Not contains in each request.
    :param queries: Optional param. Collection contains 2 date - date1
    and date2 for specify custom date range. Each of date may be None,
    or may be not. For example, if request contains 2 queries of date:
    date1=2022.12.01 and date2=2022.12.11 - in this case will be output
    statistics for date range 2022.12.01 - 2022.12.11.
    date-range statistics.
    :return: type(RequestParams)
    """
    constructor = RequestParams.construct if construct else RequestParams
    params = constructor(
        language=language,
        compare_type=compare_type,
        param1=queries.get('param1', None),
        param2=queries.get('param2', None),
    )
    return params


def process_data(
        language,
        compare_type=None,
        **queries,
) -> RequestParams | tuple[ResponseError, StatusCode]:  # Need to change docs!
    """Abstraction for handling requests path parts and request queries
        and validation them by BaseModel pydantic class.
        Return data in dict type"""
    try:
        params = make_request_params(
            language,
            compare_type=compare_type,
            **queries)
    except ValidationError:
        params = make_request_params(
            language,
            construct=True,
            compare_type=compare_type,
            **queries
        )
        return _get_response_error(params), status.HTTP_404_NOT_FOUND
    return params


def get_statistics(params: RequestParams) -> \
        tuple[Union[ResponseDone, list[ResponseDone], ResponseError],
              StatusCode]:

    language = get_language(params)
    compare_type = get_compare_type(params)

    if not compare_type:
        data_from_db = _get_list_data_by_language(language)
        return data_from_db, status.HTTP_200_OK

    elif compare_type == 'today':
        data_from_db = DB(language, compare_type).stat
        return _get_response_done(
            data_from_db,
            language,
            compare_type), status.HTTP_200_OK


def _get_list_data_by_language(
        language: str
) -> list[ResponseDone]:

    data: list[StatisticsORM] = DB(language).stat
    statistics = list()
    for record in data:
        statistics.append(_get_response_done(record, language))
    return statistics


def _get_response_done(
        data: StatisticsORM,
        language: str,
        compare_type: str | None = None,
) -> ResponseDone:  # Need change docs!

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


def _get_response_error(params: RequestParams) -> ResponseError:
    # Need change docs!
    """Create pydantic BaseModel of error.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""

    return ResponseError(
        errors={
            'type': 'not_found',  # Plug
            'count': 1
        },
        language=get_language(params),
        compare_type=get_compare_type(params),
        param1=get_queries(params)['param1'],
        param2=get_queries(params)['param2'],
    )
