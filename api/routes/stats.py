from loguru import logger

from fastapi import APIRouter, status
from fastapi.responses import Response
from fastapi_pagination import Page, paginate, add_pagination


from api.logic import (
    get_statistics,
    process_user_request,
    upload_statistics,
    get_list_of_response200,
    get_response_200,
)

from api.lib.base_models import Response200, Response404, RequestParams


router = APIRouter(
    prefix='/stat',
    tags=['stat']
)


@router.post('/upload')
async def upload_stats(response: Response) -> Response:

    resp = upload_statistics()
    response.status_code = status.HTTP_200_OK if resp['success'] else \
        status.HTTP_403_FORBIDDEN

    return resp


@router.get('/{language}', status_code=200, response_model=Page[Response200])
async def stat_by_language(language: str, resp: Response):

    params: RequestParams | Response404 = process_user_request(language)

    if isinstance(params, Response404):
        resp.status_code = 404
        return params

    statistics = get_statistics(params)
    response = get_list_of_response200(params, statistics)

    return paginate(response)


@router.get('/{language}/{compare_type}/', status_code=200)
async def stat_by_compare_type(
        resp: Response,
        language: str,
        compare_type: str,
        date1: str | None = None,
        date2: str | None = None,
) -> Response200 | Response404:

    params: RequestParams | Response404 = process_user_request(
        language,
        compare_type=compare_type,
        date1=date1,
        date2=date2,
    )
    logger.info(params)
    if isinstance(params, Response404):
        resp.status_code = 404
        return params

    statistics = get_statistics(params)
    response = get_response_200(params, statistics)

    return response


add_pagination(router)
