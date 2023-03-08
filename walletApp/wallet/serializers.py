from rest_framework import serializers
from wallet import models as wallet_models


class WalletBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = wallet_models.UserWalletBox
        fields = "__all__"


class ReadWalletBoxSerializer(serializers.ModelSerializer):

    class Meta:
        model = wallet_models.UserWalletBox
        fields = "__all__"


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = wallet_models.Entry
        fields = "__all__"

class WalletsSerializer(serializers.ModelSerializer):

    class Meta:
        model = wallet_models.Wallets
        fields = "__all__"


class ReadWalletsSerializer(serializers.ModelSerializer):
    withdrawal_pin = serializers.SerializerMethodField()
    wallet_accounts = serializers.SerializerMethodField()
    withdrawable = serializers.SerializerMethodField()

    class Meta:
        model = wallet_models.Wallets
        fields = "__all__"

    def get_withdrawal_pin(self, obj):
        withdrawal_pin = wallet_models.UserWalletPinModel \
                                .objects.filter(user=obj.walletBox.user)
        if withdrawal_pin.exists():
            return True
        return False

    def get_wallet_accounts(self, obj):
        wallet_accounts = wallet_models.UserBankAccount \
                                .objects.filter(wallet=obj)
        if wallet_accounts.exists():
            accounts = []
            for i in wallet_accounts:
                account_data = {
                    "id": i.id,
                    "account_details": i.account_details,
                    "bank": i.bank
                }
                accounts.append(account_data)
            return accounts
        return []

    def get_withdrawable(self, obj):
        return obj.walletBox.withdrawable
        



class WalletTransferSerializer(serializers.Serializer):
    receiver = serializers.EmailField(required=True)
    currency = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    reference = serializers.CharField(required=True)


class WalletManualEntrySerializer(serializers.Serializer):
    user = serializers.EmailField(required=True)
    currency = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    reference = serializers.CharField(required=True)
    entry_type = serializers.CharField(required=True)
    description = serializers.CharField(required=True)


class TXWalletManualEntrySerializer(serializers.Serializer):
    currency = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    reference = serializers.CharField(required=True)
    entry_type = serializers.CharField(required=True)
    description = serializers.CharField(required=True)


class WalletManualAvailableEntrySerializer(serializers.Serializer):
    user = serializers.EmailField(required=True)
    currency = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    reference = serializers.CharField(required=True)
    entry_type = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    balance_wallet = serializers.BooleanField(required=False)


class UserBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = wallet_models.UserBankAccount
        fields = "__all__"


class UserWalletTopUpSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)
    currency = serializers.CharField(required=True)
    reference = serializers.CharField(required=True)


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = wallet_models.UserWalletWithdrawalRequest
        fields = '__all__'


class UserWalletPinSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(required=True,)
    class Meta:
        model = wallet_models.UserWalletPinModel
        fields = "__all__"

class ValidateUserWalletPinSerializer(serializers.Serializer):
    user = serializers.UUIDField(required=True)
    pin = serializers.CharField(required=True)


class PinSerializer(serializers.Serializer):
    pin = serializers.CharField(required=True, max_length = 1000)

class PinValidateSerializer(serializers.Serializer):
    user  = serializers.UUIDField(required=True)
    reset_code = serializers.CharField(required=True, max_length = 1000)

class PinResetSerializer(serializers.Serializer):
    user  = serializers.UUIDField(required=True)
    pin = serializers.CharField(required=True)
    confirm_pin = serializers.CharField(required=True)


# admin reset serializer
class AdminPinResetSerializer(serializers.Serializer):
   user  = serializers.UUIDField(required=True)


class AdminActivateBusinessDriverWithdrawalsSerializer(serializers.Serializer):
   business  = serializers.UUIDField(required=True)
   

class ChangePinSerializer(serializers.Serializer):
    user  = serializers.UUIDField(required=True)
    old_pin = serializers.CharField(required=True)
    pin = serializers.CharField(required=True)
    confirm_pin = serializers.CharField(required=True)


class InterCurrencyTransfer(serializers.Serializer):
    receiver = serializers.EmailField(required=True)
    from_currency = serializers.CharField(required=True)
    to_currency = serializers.CharField(required=True)
    amount = serializers.FloatField(required=True)
    reference = serializers.CharField(required=True)