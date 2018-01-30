from app.settings.dev import *

# Used for external django apps like the scraper

INSTALLED_APPS = [
    'partisk.apps.PartiskConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
