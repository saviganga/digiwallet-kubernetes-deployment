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
            "HOST": "dbWallet",
            "PORT": 5432,
        },

        "auth": {        
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('AUTH_POSTGRES_DB'),
            "USER": os.environ.get('AUTH_POSTGRES_USER'),
            "PASSWORD": os.environ.get('AUTH_POSTGRES_PASSWORD'),
            "HOST": "dbAuth",
            "PORT": 5432,
        },

        "config": {        
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('CONFIG_POSTGRES_DB'),
            "USER": os.environ.get('CONFIG_POSTGRES_USER'),
            "PASSWORD": os.environ.get('CONFIG_POSTGRES_PASSWORD'),
            "HOST": os.environ.get('CONFIG_POSTGRES_HOST'),
            "PORT": 5432,
        },
    }

