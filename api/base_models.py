from typing import Literal
from pydantic import BaseModel
from typing import TypedDict, NamedTuple
from api.orm_models import StatisticsORM


class RequestParams(BaseModel):
    language: Literal['python', 'java', 'javascript', 'php', 'ruby']
    compare_type: Literal['today', 'week', 'month'] | None
    param1: str | None
    param2: str | None


class Response200(NamedTuple):
    language: str
    date: str
    vacancies: int
    no_experience: int
    region: int
    site: int
    compare_type: str | None


class CTResponse200(NamedTuple):
    language: str
    compare_type: str
    date_ct: str
    date_now: str
    jobs_were: int
    jobs_now: int
    comparison: dict[str, int]


class Response404(NamedTuple):
    errors: dict[str, str]
    language: str
    compare_type: str | None
    param1: str | None
    param2: str | None


class Statistics(TypedDict):
    today: StatisticsORM | None
    ct_stat: StatisticsORM | None
    array_stat: list[StatisticsORM] | None
