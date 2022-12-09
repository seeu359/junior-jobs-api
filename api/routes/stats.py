from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.services import get_processed_data
from api.services import get_request_data
from loguru import logger

router = APIRouter(
    prefix='/stat',
    tags=['stat'],
)


@router.get('/{language}')
async def stat_by_language(
        language: str,
        date1: str | None = None,
        date2: str | None = None,
) -> JSONResponse:

    data = get_request_data(language, param1=date1, param2=date2)
    response_data, status_code = get_processed_data(data)

    logger.error(response_data)
    return JSONResponse(
        content=response_data,
        status_code=status_code
    )


@router.get('/{language}/{compare_type}')
async def stat_by_compare_type(
        language: str, compare_type: str
) -> JSONResponse:

    data = get_request_data(language, compare_type)
    response_data, status_code = get_processed_data(data)

    return JSONResponse(
        response_data,
        status_code=status_code,
    )
