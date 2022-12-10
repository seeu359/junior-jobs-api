from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.services import get_statistics, RequestParams, process_data
from loguru import logger

router = APIRouter(
    prefix='/stat',
    tags=['stat'],
)


@router.get('/{language}')
async def stat_by_language(language: str) -> JSONResponse:

    params: RequestParams = process_data(language)
    response_data, status_code = get_statistics(params)

    logger.error(response_data)
    return JSONResponse(
        content=response_data,
        status_code=status_code
    )


@router.get('/{language}/{compare_type}')
async def stat_by_compare_type(
        language: str,
        compare_type: str,
        date1: str | None = None,
        date2: str | None = None,
) -> JSONResponse:

    params: RequestParams = process_data(
        language,
        compare_type=compare_type,
        param1=date1,
        param2=date2,
    )
    response_data, status_code = get_statistics(params)

    return JSONResponse(
        response_data,
        status_code=status_code,
    )
