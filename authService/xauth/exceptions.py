from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied,
    NotAuthenticated,
)


class TokenExpired(NotAuthenticated):
    status_code = 403
    default_detail = "Access token expired"
    default_code = "forbidden"


class ClientNotFound(NotAuthenticated):
    status_code = 403
    default_detail = "Client not found"
    default_code = "forbidden"


class UserNotFound(NotAuthenticated):
    status_code = 401
    default_detail = "Invalid login details"
    default_code = "unauthorized"


class InvalidJwtToken(NotAuthenticated):
    status_code = 401
    default_detail = "Authentication failed"
    default_code = "forbidden"


class InvalidPassword(NotAuthenticated):
    status_code = 401
    default_detail = "Unable to login with the provided credentials."
    default_code = "unauthorized"
