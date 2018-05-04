import os
from app.settings.common import *

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'partisk.nu']

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
]

DEBUG = os.environ.get('DEBUG') == 'True'
COMPRESS_ENABLED = os.environ.get('COMPRESS') == 'True'

VIEW_CACHE_TIME = 0
CACHE_MIDDLEWARE_SECONDS = VIEW_CACHE_TIME

CACHES = {
    'default':  {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': VIEW_CACHE_TIME,
    },
    'images': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '127.0.0.1:11211',
        'OPTIONS': {'MAX_ENTRIES': 2},
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'partisk',
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '3306')
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY', '')

ADMIN_ENABLED = os.environ.get('ADMIN_ENABLED') == 'True'
