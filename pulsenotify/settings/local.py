import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env.local')

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']