import os
from celery import Celery


if os.environ.get("ENVIRONMENT") == "LOCAL":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authService.settings.dev")
elif os.environ.get("ENVIRONMENT") == "STAGING":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authService.settings.dev")
elif os.environ.get("ENVIRONMENT") == "PRODUCTION":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authService.settings.prod")

app = Celery('authService')


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()