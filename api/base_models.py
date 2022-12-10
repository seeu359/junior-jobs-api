from typing import Literal
from pydantic import BaseModel
from typing import TypedDict


class RequestParams(BaseModel):
    language: Literal['python', 'java', 'javascript', 'php', 'ruby']
    compare_type: Literal['today', 'perweek'] | None
    param1: str | None
    param2: str | None


class ResponseDone(TypedDict):
    language: str
    date: str
    vacancies: int
    no_experience: int
    region: int
    site: int
    compare_type: str | None


class ResponseError(TypedDict):
    errors: dict[str, str]
    language: str
    compare_type: str | None
    param1: str | None
    param2: str | None


def func(a, b, **kwargs):
    return {**kwargs}
