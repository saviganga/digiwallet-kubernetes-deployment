from rest_framework import permissions
from xauth import utils as xauth_utils



# WALLETBOX
class UserWalletBoxPermissions(permissions.BasePermission):

    not_user_actions = ['manual_entry', 'update', 'partial_update', 'manual_entry_tx']

    def has_permission(self, request, view):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid:
                return False
            return True
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid or valid_user.email != obj.user:
                return False
            return True
        else:
            return False


class AdminWalletBoxPermissions(permissions.BasePermission):

    admin_actions = ['create', 'list', 'manual_entry', 'retrieve', 'inter_currency_transfer']

    def has_permission(self, request, view):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
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


# ENTRIES
class UserWalletEntriesPermissions(permissions.BasePermission):

    not_user_actions = ['manual_entry', 'create', 'update', 'partial_update', 'manual_entry_tx']

    def has_permission(self, request, view):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid:
                return False
            return True
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid or valid_user.email != obj.wallet.walletBox.user:
                return False
            return True
        else:
            return False


class AdminWalletEntriesPermissions(permissions.BasePermission):

    admin_actions = ['create', 'list', 'manual_entry', 'retrieve']

    def has_permission(self, request, view):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
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



# WALLETS
class UserWalletsPermissions(permissions.BasePermission):


    not_user_actions = ['update', 'partial_update', 'stats']

    def has_permission(self, request, view):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid:
                return False
            return True
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
            is_valid, valid_user = xauth_utils.connect.validate_token(jwt_token)
            if not is_valid or valid_user.email != obj.walletBox.user:
                return False
            return True
        else:
            return False

class AdminWalletsPermissions(permissions.BasePermission):

    admin_actions = ['list', 'retrieve', 'stats', 'admin_activate_driver_wallet_withdrawal','admin_deactivate_driver_wallet_withdrawal']

    def has_permission(self, request, view):
        if request.headers and request.headers.get('authorization'):
            jwt_token = request.headers.get('authorization')
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


# BANK ACCOUNTS

class UserBankAccountsPermissions(permissions.BasePermission):
    admin_actions = ['list', 'retrieve']
    not_user_actions = ['stats']
    businessmember_actions = []

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if view.action not in self.not_user_actions:
                return True
        return False

    def has_object_permission(self, request, view, object):
        if view.action in self.not_user_actions:
            return False
        if request.user == object.wallet.walletBox.user:
            return True
        return False

class AdminBankAccountPermissions(permissions.BasePermission):
    admin_actions = ['valid_banks', 'list', 'retrieve', 'stats']
    not_user_actions = []
    businessmember_actions = []

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_staff and 'admin' in request.headers:
            if view.action in self.admin_actions:
                return True
        return False

    def has_object_permission(self, request, view, object):
        if request.user.is_staff and 'admin' in request.headers:
            if view.action in self.admin_actions:
                return True
        return False 

