from rest_framework import permissions
from xauth import utils as xauth_utils

class AdminPermissions(permissions.BasePermission):

    print('perm')

    def has_permission(self, request, view):
        print('isson')
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            print(jwt_token)
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid or valid_user.is_staff != True:
                return False
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid or valid_user.is_staff != True:
                return False
            return True
        else:
            return False
