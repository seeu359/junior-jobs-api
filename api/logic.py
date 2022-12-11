from pydantic import ValidationError
from api.db_logic import DB
from api.services import make_request_params, get_response_error
from api.base_models import ResponseDone, ResponseError, RequestParams
from loguru import logger


def process_data(
        language,
        compare_type=None,
        **queries,
) -> RequestParams | ResponseError:  # Need to change docs!
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
        return get_response_error(params)
    return params


def get_statistics(params: RequestParams) -> ResponseDone | list[ResponseDone]:
    statistics = DB(params).stat
    logger.info(statistics)
    return statistics
