from fastapi import FastAPI
from api.routes import main_page
from api.routes import stats

app = FastAPI()
app.include_router(stats.router)
app.include_router(main_page.router)