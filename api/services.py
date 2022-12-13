from api import orm_models as om
from api.base_models import RequestParams, Response200, Response404, \
    CTResponse200, Statistics

COEFFICIENT = 100


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


def get_response_200(
        params: RequestParams,
        statistics: Statistics,
) -> Response200 | list[Response200] | CTResponse200:  # Need change docs!

    """Create pydantic BaseModel with responses data.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""
    if params.compare_type == 'today':
        today = statistics['today']
        return Response200(
            language=params.language,
            compare_type=params.compare_type,
            date=str(today.date),
            vacancies=today.vacancies,
            no_experience=today.no_experience,
            region=today.region_id,
            site=today.site_id,
        )
    if not params.compare_type:
        stat_array: list[om.StatisticsORM] = statistics['array_stat']
        result = list()
        for stat in stat_array:
            result.append(Response200(
                language=params.language,
                compare_type=params.compare_type,
                date=str(stat.date),
                vacancies=stat.vacancies,
                no_experience=stat.no_experience,
                region=stat.region_id,
                site=stat.site_id,
            ))
        return result

    else:
        today = statistics['today']
        ct_stat = statistics['ct_stat']
        stats = _compute_stat(today, ct_stat)
        return CTResponse200(
            language=params.language,
            compare_type=params.compare_type,
            date_ct=str(ct_stat.date),
            date_now=str(today.date),
            jobs_were=ct_stat.vacancies,
            jobs_now=today.vacancies,
            comparison={
                'in_amount': stats['in_amount'],
                'in_percent': stats['in_percent'],
            }
        )


def get_response_404(params: RequestParams) -> Response404:
    # Need change docs!
    """Create pydantic BaseModel of error.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""
    return Response404(
        errors={
            'type': 'not_found',  # Plug
            'count': 1
        },
        language=get_language(params),
        compare_type=get_compare_type(params),
        param1=get_queries(params)['param1'],
        param2=get_queries(params)['param2'],
    )


def _compute_stat(now: om.StatisticsORM, ct_stat: om.StatisticsORM) \
        -> dict[str, int]:
    in_amount = now.vacancies - ct_stat.vacancies
    in_percents = round(now.vacancies / ct_stat.vacancies *
                        COEFFICIENT - COEFFICIENT)
    return {
        'in_amount': in_amount,
        'in_percent': in_percents,
    }
