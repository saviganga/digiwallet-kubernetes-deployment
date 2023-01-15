from .base import *
import os
import sys


DEBUG = True  # to be changed back
SECRET_KEY = os.environ.get('SECRET_KEY')


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
            "HOST": "dbAuth",
            "PORT": 5432,
        },

        "config": {        
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('CONFIG_POSTGRES_DB'),
            "USER": 'digi-wallet-config',
            "PASSWORD": os.environ.get('CONFIG_POSTGRES_PASSWORD'),
            "HOST": "dbCo",
            "PORT": 5432,
        },

    }

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')