from .base import *
import os
import sys


DEBUG = True  # to be changed back
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ["*"]


if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {

        "default": {        
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('POSTGRES_DB'),
            "USER": os.environ.get('POSTGRES_USER'),
            "PASSWORD": os.environ.get('POSTGRES_PASSWORD'),
            "HOST": os.environ.get('POSTGRES_HOST'),
            "PORT": 5432,
        },

        "auth": {        
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('POSTGRES_DB'),
            "USER": os.environ.get('POSTGRES_USER'),
            "PASSWORD": os.environ.get('POSTGRES_PASSWORD'),
            "HOST": os.environ.get('POSTGRES_HOST'),
            "PORT": 5432,
        },

        
        'test': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
