from enum import unique
from locale import currency
import uuid
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from config import enums as config_enums
from django.core.validators import MaxValueValidator

from django.utils import timezone
from decimal import Decimal


# Create your models here.
class Country(models.Model):
    id = models.UUIDField(
        help_text="Unique identifier",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    country = models.CharField(
        max_length=254,
        choices=config_enums.COUNTRY,
        help_text=_("ISO 3166-1 alpha-3 formatted country code"),
    )
    currency = models.CharField(
        max_length=254,
        help_text=_("ISO 4217 formatted country currency."),
        choices=config_enums.CURRENCY,
    )

    class Meta:
        unique_together = ("country", "currency")


class SupportedCountry(models.Model):
    id = models.UUIDField(
        help_text="Unique identifier",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    country = models.OneToOneField(
        Country, on_delete=models.CASCADE, related_name="base_country"
    )
    vat_percentage = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        help_text=_(
            "Vat setting in percentage for all vatable items in the country."),
    )
    platform_fee = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        help_text=_("Fee taken by the platform on each trip in percentage"),
    )

