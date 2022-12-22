from pydantic import ValidationError
from api.exceptions import InvalidDateParams
from api.db_logic import DB
from api.services import make_request_params, get_response_404, \
    get_response_200, check_queries
from api.base_models import Response200, Response404, RequestParams, \
    Statistics


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
        return get_response_404(params, str(e))
    return params


def get_statistics(params: RequestParams) -> Response200 | list[Response200]:
    statistics: Statistics = DB(params).stat
    response = get_response_200(params, statistics)
    return response
