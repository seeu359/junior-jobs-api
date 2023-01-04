from datetime import date
from string import Template

import loguru
import requests
from pydantic import ValidationError

from api.lib import orm_models as om
from api.lib.base_models import RequestParams, Response404, Statistics
from api.lib.db_logic import DB
from api.lib.exceptions import DataAlreadyUploaded, InvalidDateParams
from api.lib.services import (get_compare_type, get_ct_response_200,
                              get_queries, get_response200_with_queries,
                              get_response_404, get_today_response_200)

######################################
# URL TEMPLATE FOR REQUESTS TO API HH
######################################
ALL_VACS_TEMPLATE = Template(
        'https://api.hh.ru/vacancies?'
        'text=$language+junior&per_page=100&area=$area_id'
)

NO_EXP_TEMPLATE = Template(
        'https://api.hh.ru/vacancies?'
        'text=$language+junior&per_page=100&'
        'area=$area_id&experience=noExperience'
)

######################################

RUSSIA_ID = 113


def process_user_request(
        language,
        compare_type=None,
        **queries,
) -> RequestParams | Response404:  # Need to change docs!
    """Abstraction for handling requests path parts and request queries
        and validation them by BaseModel pydantic class.
        Return data in dict type"""
    try:
        params = make_request_params(
            language,
            compare_type=compare_type,
            **queries)
        _check_queries(params)

    except (ValidationError, InvalidDateParams) as e:
        params = make_request_params(
            language,
            construct=True,
            compare_type=compare_type,
            **queries
        )
        error = _handle_error(e)
        return get_response_404(params, error)
    return params


#######################################
# API FOR CREATE  REQUEST PARAMETERS
#######################################

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

######################################


def get_statistics(
        params: RequestParams
) -> Statistics:

    statistics: Statistics = DB(params).stat
    return statistics


def get_response_200(params: RequestParams, statistics: Statistics):

    if get_compare_type(params) == 'today':
        return get_today_response_200(params, statistics)

    elif get_queries(params)['date1'] is not None and \
            get_queries(params)['date2'] is not None:
        return get_response200_with_queries(params, statistics)

    else:
        return get_ct_response_200(params, statistics)


def upload_statistics():
    try:
        _check_data_in_db()

        data = _get_data_from_hh_api()

        DB(RequestParams()).upload_statistics(data)

        return dict(success=True, error_message=None)

    except DataAlreadyUploaded as e_message:

        loguru.logger.info(type(e_message))
        return dict(success=False, error_message=str(e_message))


def _check_data_in_db():
    with om.session() as s:
        data = s.query(om.StatisticsORM).\
                filter(
                om.StatisticsORM.date == date.today()).first()
        if data is not None:
            raise DataAlreadyUploaded(
                'Data has been uploaded in database already today '
            )


def _check_queries(params: RequestParams):
    dates = get_queries(params)
    if not dates['date1'] and not dates['date2']:
        return
    if dates['date1'] > dates['date2']:
        raise InvalidDateParams('The transmitted time interval is incorrect')


def _handle_error(error) -> str:

    if isinstance(error, ValidationError):
        invalid_params = error.errors()[0]['ctx']['given']
        return f'Wrong parameters transmitted: {invalid_params}'

    return str(error)


def _get_data_from_hh_api(
        all_vacs_template=ALL_VACS_TEMPLATE,
        no_exp_template=NO_EXP_TEMPLATE,
) -> dict[str, tuple[int, int]]:
    """
    Request to HH API to get data about vacancies.
    :return: dict with tuple where tuple[0] - all vacancies count,
    tuple[1] - no experience required vacancies count.
    """
    languages = ['python', 'php', 'javascript', 'ruby', 'java']
    result = dict()

    for lang in languages:

        all_vacs = \
            requests.get(
                all_vacs_template.substitute(
                    language=lang, area_id=RUSSIA_ID
                )
            ).json()

        no_exp_vacs = requests.get(
            no_exp_template.substitute(
                language=lang, area_id=RUSSIA_ID
            )
        ).json()

        result[lang] = all_vacs['found'], no_exp_vacs['found']
    return result
