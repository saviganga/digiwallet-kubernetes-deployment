from django.db import models

# Create your models here.
from datetime import datetime
from email.policy import default
from pickle import TRUE
from pyexpat import model
from socket import send_fds

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import jwt
from .managers import MyUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

from decimal import Decimal

import time
from django.utils import timezone

from user import enums as user_enums

import uuid


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None

    phone = models.CharField(_("phone number"), unique=True, max_length=15)
    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(
        _("first name"),
        max_length=254,
        help_text=_("The first name as it appears on ID or passport"),
    )
    last_name = models.CharField(
        _("last name"),
        max_length=254,
        help_text=_("The first name as it appears on ID or passport"),
    )
    user_name = models.CharField(
        _("username"),
        max_length=254,
        help_text=_("unique app identifier"),
        unique=True
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )

    is_verified = models.BooleanField(
        _("user verified"),
        default=False,
        help_text=_("Designates whether the user is a verified user"),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )

    source = models.CharField(
        max_length=20,
        choices=user_enums.SOURCE,
        help_text="SignUp App",
        null=True,
        blank=True,
    )

    # (sentinel)
    supported_country = models.CharField(
        max_length=100,
        default='NGA',
        blank=False,
        null=True,
    )

    address = models.JSONField(default=dict)

    gender = models.CharField(
        _("gender"),
        max_length=20,
        blank=True,
        choices=user_enums.GENDER,
        help_text=_("User gender"),
    )

    referral_code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("User referral code"),
        null=True,
    )
    
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    social_login = models.BooleanField(null=True, blank=True, default=False)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone", "user_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-updated_on", "-date_joined"]

    def __unicode__(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.user_name}"

    def save(self, *args, **kwargs):
        self.referral_code = str(self.phone).strip("+")
        super().save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        first_name = self.first_name.strip()
        last_name = self.last_name.strip()
        full_name = f"{first_name} {last_name}"
        return full_name

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    