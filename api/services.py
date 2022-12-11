from api import orm_models as om
from api.base_models import RequestParams, ResponseDone, ResponseError


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


def get_response_done(
        stat_obj: om.StatisticsORM,
        language: str,
        compare_type: str | None = None,
) -> ResponseDone:  # Need change docs!

    """Create pydantic BaseModel with responses data.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""

    return ResponseDone(
        language=language,
        date=str(stat_obj.date),
        vacancies=stat_obj.vacancies,
        no_experience=stat_obj.no_experience,
        region=stat_obj.region_id,
        site=stat_obj.site_id,
        compare_type=compare_type,
    )


def get_response_error(params: RequestParams) -> ResponseError:
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
