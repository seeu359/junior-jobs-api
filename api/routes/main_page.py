from fastapi import APIRouter

router = APIRouter()


@router.get('/', status_code=200)
async def root():
    return {'success': True}
