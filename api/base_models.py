from typing import Literal
from pydantic import BaseModel
from typing import TypedDict
from api.orm_models import StatisticsORM


class RequestParams(BaseModel):
    language: \
        Literal['python', 'ruby', 'javascript', 'java', 'php'] | None = None
    compare_type: Literal['today', 'week', 'month', 'custom'] | None = None
    date1: str | None = None
    date2: str | None = None


class Response200(BaseModel):
    language: str
    date: str
    vacancies: int
    no_experience: int
    region: int
    site: int
    compare_type: str | None


class CTResponse200(BaseModel):
    language: str
    compare_type: str
    date1: str
    date2: str
    vacs_were: int
    vacs_became: int
    comparison: dict[str, int]


class Response404(BaseModel):
    errors: str
    language: str
    compare_type: str | None
    date1: str | None
    date2: str | None


class Statistics(TypedDict):
    today: StatisticsORM | None
    ct_stat: StatisticsORM | None
    array_stat: list[StatisticsORM] | None
    custom_stat: dict[str, StatisticsORM | None] | None
