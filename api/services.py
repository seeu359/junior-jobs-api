from api import orm_models as om
from pydantic import ValidationError
from api.exceptions import InvalidDateParams
from api.base_models import RequestParams, Response200, Response404, \
    CTResponse200, Statistics

COEFFICIENT = 100


def get_language(params: RequestParams) -> str | None:
    """
    Selector for receive language from RequestParams
    :param params: type(RequestParams)
    :return: str
    """
    return params.language


def get_compare_type(params: RequestParams) -> str | None:
    """
    Selector for receive compare_type from RequestParams
    :param params: RequestParams
    :return: str
    """
    return params.compare_type


def get_queries(params: RequestParams) -> dict[str | None, str | None]:
    """
    Selector for receive queries from RequestParams
    :param params: RequestParams
    :return: str
    """
    return {
        'date1': params.date1,
        'date2': params.date2,
    }


def check_queries(params: RequestParams):
    dates = get_queries(params)
    if not dates['date1'] and not dates['date2']:
        return
    if dates['date1'] > dates['date2']:
        raise InvalidDateParams('The transmitted time interval is incorrect')


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
        date1=queries.get('date1', None),
        date2=queries.get('date2', None),
    )
    return params


def get_response_200(params: RequestParams, statistics: Statistics):
    if get_compare_type(params) == 'today':
        return _get_today_response_200(params, statistics)
    elif get_compare_type(params) is None:
        return _get_list_of_response200(params, statistics)
    elif get_queries(params)['date1'] is not None and \
            get_queries(params)['date2'] is not None:
        return _get_response200_with_queries(params, statistics)
    else:
        return _get_ct_response_200(params, statistics)


def _get_today_response_200(
        params: RequestParams,
        statistics: Statistics,
) -> Response200 | list[Response200] | CTResponse200:  # Need change docs!

    """Create pydantic BaseModel with responses data.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""
    today = statistics['today']
    return Response200(
        language=get_language(params),
        compare_type=get_compare_type(params),
        date=str(today.date),
        vacancies=today.vacancies,
        no_experience=today.no_experience,
        region=today.region_id,
        site=today.site_id,
    )


def _get_list_of_response200(
        params: RequestParams,
        statistics: Statistics) -> list[Response200]:
    stat_list: list[om.StatisticsORM] = statistics['array_stat']
    result = list()
    for stat in stat_list:
        result.append(Response200(
            language=get_language(params),
            compare_type=get_compare_type(params),
            date=str(stat.date),
            vacancies=stat.vacancies,
            no_experience=stat.no_experience,
            region=stat.region_id,
            site=stat.site_id,
        ))
    return result


def _get_ct_response_200(
        params: RequestParams,
        statistics: Statistics) -> CTResponse200:

    date1 = statistics.get('today')
    date2 = statistics.get('ct_stat')
    stats = _compute_stat(date1, date2)
    return CTResponse200(
        language=get_language(params),
        compare_type=get_compare_type(params),
        date1=str(date1.date),
        date2=str(date2.date),
        vacs_became=date1.vacancies,
        vacs_were=date2.vacancies,
        comparison={
            'in_amount': stats['in_amount'],
            'in_percent': stats['in_percent'],
        }
    )


def _get_response200_with_queries(
        params: RequestParams,
        statistics: Statistics) -> CTResponse200:

    date1 = statistics['custom_stat']['date1']
    date2 = statistics['custom_stat']['date2']
    stats = _compute_stat(date2, date1)
    return CTResponse200(
        language=get_language(params),
        compare_type=get_compare_type(params),
        date1=str(date1.date),
        date2=str(date2.date),
        vacs_were=date1.vacancies,
        vacs_became=date2.vacancies,
        comparison={
            'in_amount': stats['in_amount'],
            'in_percent': stats['in_percent'],
        }
    )


def handle_error(error) -> str:
    if isinstance(error, ValidationError):
        invalid_params = error.errors()[0]['ctx']['given']
        return f'Wrong parameters transmitted: {invalid_params}'
    return str(error)


def get_response_404(params: RequestParams, error) -> Response404:
    # Need change docs!
    """Create pydantic BaseModel of error.
    Data from this model won't validate because data from user
    request has been checked yet! Other data comes from database and this
    data can be trusted"""
    return Response404(
        errors=error,
        language=get_language(params),
        compare_type=get_compare_type(params),
        date1=get_queries(params)['date1'],
        date2=get_queries(params)['date2'],
    )


def _compute_stat(reduced: om.StatisticsORM, reducer: om.StatisticsORM) \
        -> dict[str, int]:
    in_amount = reduced.vacancies - reducer.vacancies
    in_percents = round(reduced.vacancies / reducer.vacancies *
                        COEFFICIENT - COEFFICIENT)
    return {
        'in_amount': in_amount,
        'in_percent': in_percents,
    }
