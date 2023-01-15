from fastapi import APIRouter, status, Depends
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.bases import AbstractPage

from api.stat.services import StatServices
from api.stat import schemes

TIME_DELTA_WEEK = 7
TIME_DELTA_MONTH = 30
TIME_DELTA_3MONTH = 90
TIME_DELTA_6MONTH = 180

router = APIRouter(
    prefix='/stat',
    tags=['stat']
)


@router.post(
    '/upload',
    status_code=status.HTTP_200_OK,
)
async def upload_stats(stat_service: StatServices = Depends()) -> list:

    return stat_service.upload()


@router.get(
    '/{language}',
    status_code=status.HTTP_200_OK,
    response_model=Page[schemes.Statistics],
)
async def stat_by_language(
        language: schemes.Languages,
        stat_service: StatServices = Depends(),

) -> AbstractPage[schemes.Statistics]:

    response = stat_service.get_array_stat(language)
    return paginate(response)


@router.get(
    path='/{language}/today',
    response_model=schemes.Statistics,
    status_code=status.HTTP_200_OK,
)
async def today_stat(
        language: schemes.Languages,
        services: StatServices = Depends(),
) -> schemes.Statistics:

    return services.get_today_stat(language)


@router.get(
    path='/{language}/week',
    response_model=schemes.CTStatistics,
    status_code=status.HTTP_200_OK,
)
async def week_stat(
        language: schemes.Languages,
        services: StatServices = Depends(),
) -> schemes.CTStatistics:

    return services.get_stat_by_compare_type(
        language, (TIME_DELTA_WEEK, 'week',)
    )


@router.get(
    path='/{language}/month',
    response_model=schemes.CTStatistics,
    status_code=status.HTTP_200_OK,
)
async def month_stat(
        language: schemes.Languages,
        services: StatServices = Depends(),
) -> schemes.CTStatistics:

    return services.get_stat_by_compare_type(
        language, (TIME_DELTA_MONTH, 'month',)
    )


@router.get(
    path='/{language}/3month',
    response_model=schemes.CTStatistics,
    status_code=status.HTTP_200_OK,
)
async def three_month_stat(
        language: schemes.Languages,
        services: StatServices = Depends(),
) -> schemes.CTStatistics:

    return services.get_stat_by_compare_type(
        language, (
            TIME_DELTA_3MONTH, '3month',)
    )


@router.get(
    path='/{language}/6month',
    response_model=schemes.CTStatistics,
    status_code=status.HTTP_200_OK,
)
async def six_month_stat(
        language: schemes.Languages,
        services: StatServices = Depends(),
) -> schemes.CTStatistics:

    return services.get_stat_by_compare_type(
        language, (
            TIME_DELTA_3MONTH, '6month',)
    )


@router.get(
    path='/{language}/year',
    response_model=schemes.CTStatistics,
    status_code=status.HTTP_200_OK,
)
async def year_stat(
        language: schemes.Languages,
        services: StatServices = Depends(),
) -> schemes.CTStatistics:

    return services.get_stat_by_compare_type(
        language, (
            TIME_DELTA_3MONTH, 'year',)
    )


add_pagination(router)
