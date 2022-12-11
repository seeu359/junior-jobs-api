from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from api.logic import get_statistics, RequestParams, process_data, \
    ResponseError, ResponseDone
from loguru import logger

router = APIRouter(
    prefix='/stat',
    tags=['stat'],
)


@router.get('/{language}')
async def stat_by_language(language: str) -> JSONResponse:

    params: RequestParams | ResponseError = process_data(language)
    if isinstance(params, ResponseError):
        return JSONResponse(
            content=params._asdict(),
            status_code=status.HTTP_404_NOT_FOUND
        )
    response_done: ResponseDone = get_statistics(params)

    logger.error(response_done)
    return JSONResponse(
        content=response_done,
        status_code=status.HTTP_200_OK
    )


@router.get('/{language}/{compare_type}')
async def stat_by_compare_type(
        language: str,
        compare_type: str,
        date1: str | None = None,
        date2: str | None = None,
) -> JSONResponse:

    params: RequestParams | ResponseError = process_data(
        language,
        compare_type=compare_type,
        param1=date1,
        param2=date2,
    )
    if isinstance(params, ResponseError):
        return JSONResponse(
            content=params._asdict(),
            status_code=status.HTTP_404_NOT_FOUND
        )
    response_done: ResponseDone = get_statistics(params)

    return JSONResponse(
        content=response_done._asdict(),
        status_code=status.HTTP_200_OK,
    )
