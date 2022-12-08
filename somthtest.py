from pydantic import BaseModel
from typing import Literal


class CompareTypes(BaseModel):
    compare_type: Literal[
        'today',
        'perweek',
        'permonth',
        'per3month',
        'per6month',
        'peryear',
                  ] | None
