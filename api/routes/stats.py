from loguru import logger

from fastapi import APIRouter, status
from fastapi.responses import Response
from fastapi_pagination import Page, paginate, add_pagination


from api.logic import get_statistics, process_user_request, upload_statistics
from api.base_models import Response200, Response404, RequestParams


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
async def stat_by_language(language: str, response: Response):

    params: RequestParams | Response404 = process_user_request(language)

    if isinstance(params, Response404):
        response.status_code = 404
        return params

    response_done: list[Response200] = get_statistics(params)

    return paginate(response_done)


@router.get('/{language}/{compare_type}/', status_code=200)
async def stat_by_compare_type(
        response: Response,
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
        response.status_code = 404
        return params

    response_done: Response200 = get_statistics(params)

    return response_done


add_pagination(router)
