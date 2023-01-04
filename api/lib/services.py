from api.lib import orm_models as om
from api.lib.base_models import (CTResponse200, RequestParams, Response200,
                                 Response404, Statistics)

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


def get_today_response_200(
        params: RequestParams,
        statistics: Statistics,
) -> Response200 | list[Response200] | CTResponse200 | CTResponse200:

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


def get_list_of_response200(
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


def get_ct_response_200(
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


def get_response200_with_queries(
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
