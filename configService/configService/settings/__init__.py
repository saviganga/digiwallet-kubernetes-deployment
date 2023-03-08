"""

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

load_dotenv()

from django.core.wsgi import get_wsgi_application

if os.environ.get("ENVIRONMENT") == "LOCAL":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configService.settings.dev")
elif os.environ.get("ENVIRONMENT") == "STAGING":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configService.settings.dev")
elif os.environ.get("ENVIRONMENT") == "PRODUCTION":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configService.settings.prod")


application = get_wsgi_application()
