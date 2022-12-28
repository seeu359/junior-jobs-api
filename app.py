from fastapi import FastAPI
from api.routes import main_page
from api.routes import stats

"""
Entry point
"""

app = FastAPI()
app.include_router(stats.router)
app.include_router(main_page.router)
