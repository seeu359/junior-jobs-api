from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

router = APIRouter()
templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        'base.html', {'request': request}
    )
