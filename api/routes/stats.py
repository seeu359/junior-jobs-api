from fastapi import APIRouter
from fastapi.responses import Response
from ..db_logic import get_processed_data, ResponseData
from pydantic import BaseModel
from typing import Literal


router = APIRouter(
    prefix='/stat',
    tags=['stat'],
)


class Languages(BaseModel):
    language: Literal[
        'python',
        'ruby',
        'javascript',
        'java',
        'php',
    ]


class CompareTypes(BaseModel):
    compare_type: Literal[
        'today',
        'perweek',
        'permonth',
        'per3month',
        'per6month',
        'peryear',
                  ] | None


@router.get('/{language}/{compare_type}')
async def stat(language: str, compare_type: str) -> ResponseData:
    data = {
        'language': language,
        'compare_type': compare_type,
        }
    response_data: ResponseData = get_processed_data(data)
    return response_data
