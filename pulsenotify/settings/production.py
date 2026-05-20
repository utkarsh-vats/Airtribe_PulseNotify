import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env.prod')

from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

CSRF_TRUSTED_ORIGINS = ['https://api.pulsenotify.obtuse.in']

CORS_ALLOWED_ORIGINS = [
    'https://localhost:3000',
    'https://pulsenotify.obtuse.in',
    'https://pulsenotify.vercel.app',
]

STATIC_ROOT = BASE_DIR / 'static'