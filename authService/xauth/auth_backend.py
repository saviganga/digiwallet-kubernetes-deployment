from urllib import request
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from xauth import utils as xauth_utils
from rest_framework.authentication import BaseAuthentication
from xauth import exceptions as xauth_exceptions



class JWTAuthentication(BaseAuthentication):
    def __init__(self, realm="API"):
        self.realm = realm

    def authenticate(self, request, **kwargs):
        """[Function to extract jwt token for an header]

        Arguments:
            request {[type] -- [description]}

        Returns:
            [token] -- [userobj]
        """
        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION", None)
            if auth_header:
                auth_method, auth_token = auth_header.split(" ", 1)
                if not auth_token:
                    return None
                if not auth_method.lower() == "jwt":
                    return None
                user = JWTAuthentication.verify_access_token(auth_token)
                return user, None
            else:
                return AnonymousUser(), None

        except:
            pass

    def verify_access_token(auth_token):
        """[verify and decode the jwt token  provided]

        Arguments:
            auth_token {[token]} -- [jwt_token]

        Returns:
            [user] -- [user obj]
        """
        payload, user = xauth_utils.decode_jwt(auth_token)
        return user
