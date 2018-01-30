from app.settings.common import *

ALLOWED_HOSTS = ['localhost']

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'table name',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': ''
    }
}

SECRET_KEY = 'xxxxx'

DEBUG = False
COMPRESS_ENABLED = True

VIEW_CACHE_TIME = 0
CACHE_MIDDLEWARE_SECONDS = VIEW_CACHE_TIME

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    'LOCATION': '127.0.0.1:11211',
    'TIMEOUT': VIEW_CACHE_TIME,
}
