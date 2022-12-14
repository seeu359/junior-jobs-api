import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SQLITE = 'sqlite:///' + str(BASE_DIR) + '/db.sqlite'

POSTGRES = os.getenv('PGCONNECT')

DEBUG = os.getenv('DEBUG', False)

DATABASE = SQLITE if DEBUG else POSTGRES
