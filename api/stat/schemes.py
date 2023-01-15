import datetime
from enum import Enum

from pydantic import BaseModel


class BaseStatistics(BaseModel):
    language: str
    compare_type: str


class Statistics(BaseStatistics):

    date: datetime.date
    vacancies: int
    no_experience: int
    region: int
    site: int

    class Config:

        orm_mode = True


class CTStatistics(BaseStatistics):

    vacs_were: int
    vacs_became: int
    comparison: dict


class Languages(str, Enum):

    python = 'python'
    php = 'php'
    javascript = 'javascript'
    ruby = 'ruby'
    java = 'java'
