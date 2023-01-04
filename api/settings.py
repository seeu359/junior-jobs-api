import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

PATH_TO_LOGS = BASE_DIR / 'api' / 'logs' / 'logs.log'

LOGGER_FORMAT = '{time:YYYY.MM.DD - HH:mm:ss} - {level} - {message} '

LOGGER = logger.add(
    sink=PATH_TO_LOGS,
    level='INFO',
    format=LOGGER_FORMAT,
)


SQLITE = 'sqlite:///' + str(BASE_DIR) + '/db.sqlite'

POSTGRES = os.getenv('PGCONNECT')

DEBUG = os.getenv('DEBUG', False)

DATABASE = SQLITE if DEBUG else POSTGRES
