import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env.prod')

from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

CSRF_TRUSTED_ORIGINS = ['https://api.pulsenotify.obtuse.in']

STATIC_ROOT = BASE_DIR / 'static'