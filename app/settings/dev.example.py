from app.settings.common import *

ALLOWED_HOSTS = ['*']

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

SECRET_KEY = 'n)r(4l+x_xbu*0pin)#%$czk+lly&79&nw#5k5+8qe*opf&@au'

DEBUG = True
COMPRESS_ENABLED = False

VIEW_CACHE_TIME = 0
CACHE_MIDDLEWARE_SECONDS = VIEW_CACHE_TIME

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'images': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '127.0.0.1:11211',
        'OPTIONS': {'MAX_ENTRIES': 2},
    }
}

ADMIN_ENABLED = True
