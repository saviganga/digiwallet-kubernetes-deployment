from django.contrib import admin
from config import models as config_models  #allows access to our custom user model


# Register your models here.
admin.site.register(config_models.Country)
admin.site.register(config_models.SupportedCountry)