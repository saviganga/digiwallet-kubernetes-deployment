import datetime
from lib2to3.pgen2 import token
from pickle import NONE
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import jwt
import random
import string
from xauth import models as xauth_models
from user import models as user_models
from xauth import exceptions as xauth_exceptions
from xauth import models as xauth_models


def find_user(email=None, username=None, phone=None) -> user_models.CustomUser:
    """
    [Find user by email or phone number]
    """
    if email == None and username == None and phone == None:
        raise xauth_exceptions.UserNotFound
    elif username:
        try:
            user = user_models.CustomUser.objects.get(user_name=username)
            return user
        except:
            raise xauth_exceptions.UserNotFound
    elif email:
        try:
            user = user_models.CustomUser.objects.get(email=email)
            return user
        except:
            raise xauth_exceptions.UserNotFound
    elif phone:
        try:
            user = user_models.CustomUser.objects.get(phone=phone)
            return user
        except:
            raise xauth_exceptions.UserNotFound
    else:
        raise xauth_exceptions.UserNotFound


def encode_jwt(user, hours,  platform="WEB", reaml="API"):
    """
    Generates Auth Token
    :return: string
    """
    token = xauth_models.AuthToken.objects.create(
        token="".join(random.choice(string.ascii_letters) for i in range(7)),
        user_id=user.id,
        platform=platform,
        expiry_date = timezone.now() + datetime.timedelta(hours=hours)
    )
    payload = {
        "exp": timezone.now() + datetime.timedelta(hours=hours),
        "iat": timezone.now(),
        "sub": str(user.id),
        "token": token.token,
        "permission": {
            "is_staff": user.is_staff,
        },
        "platform": platform
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def regenerate_jwt(user, hours,  platform, token):
    """
    Re-generates Auth Token
    :return: string
    """
    payload = {
        "exp": timezone.now() + datetime.timedelta(hours=hours),
        "iat": timezone.now(),
        "sub": str(user.id),
        "token":token,
        "permission": {
            "is_staff": user.is_staff,
        },
        "platform": platform
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def decode_jwt(jwt_token) -> dict:
    """
    Validates the auth token and return encoded payload
    :param auth_token:
    :return: bool|dict
    """
    try:
        payload = jwt.decode(
            jwt_token, settings.JWT_SECRET_KEY, algorithms="HS256")
        auth_token = xauth_models.AuthToken.objects.filter(
            token=payload["token"])
        if not auth_token.exists():
            raise xauth_exceptions.InvalidJwtToken
        else:
            return payload, auth_token.first().user
    # except jwt.ExpiredSignatureError:
    #     xauth_models.AuthToken.objects.filter(token=jwt_token).delete()
    #     raise xauth_exceptions.InvalidJwtToken
    except:
        raise xauth_exceptions.InvalidJwtToken


def destroy_jwt(jwt_token: str, all=False):
    """
    Validate jwt token and delete token from the database
    :param jwt_token: str
    :param all: bool
    """
    payload, user = decode_jwt(jwt_token)
    token = payload["token"]
    if all:
        xauth_models.AuthToken.objects.filter(user_id=payload["sub"]).delete()
    else:
        xauth_models.AuthToken.objects.filter(token=token).delete()
