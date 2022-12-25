import loguru
import requests
from datetime import date
from string import Template
from pydantic import ValidationError
from api.db_logic import DB
from api import orm_models as om
from api.exceptions import InvalidDateParams, DataAlreadyUploaded
from api.services import make_request_params, get_response_404, \
    get_response_200, check_queries, handle_error
from api.base_models import Response200, Response404, RequestParams, \
    Statistics


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
        check_queries(params)

    except (ValidationError, InvalidDateParams) as e:
        params = make_request_params(
            language,
            construct=True,
            compare_type=compare_type,
            **queries
        )
        error = handle_error(e)
        return get_response_404(params, error)
    return params


def get_statistics(params: RequestParams) -> Response200 | list[Response200]:
    statistics: Statistics = DB(params).stat
    response = get_response_200(params, statistics)
    return response


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


def _get_data_from_hh_api() -> dict[str, tuple[int, int]]:
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
                ALL_VACS_TEMPLATE.substitute(language=lang, area_id=113)
            ).json()
        no_exp_vacs = requests.get(
            NO_EXP_TEMPLATE.substitute(language=lang, area_id=113)
        ).json()
        result[lang] = all_vacs['found'], no_exp_vacs['found']
    return result
