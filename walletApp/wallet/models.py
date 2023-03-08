from email.policy import default
from enum import unique
from random import choices
from time import time
import uuid
from importlib import import_module
from typing import AnyStr, Dict, Union
from decimal import Decimal
from django.db import IntegrityError, models

from wallet import enums as wallet_enums
from datetime import datetime as dt





# Create your models here.


class Wallets(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for each user wallet",
    )
    walletBox = models.ForeignKey(
        "wallet.UserWalletBox", related_name="wallets", on_delete=models.CASCADE
    )
    currency = models.CharField(max_length=1024)
    balance = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, help_text="Wallet balance"
    )
    available = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, help_text="Wallet available balance"
    )
    description = models.CharField(
        max_length=250, blank=True, null=True, help_text="Wallet description"
    )
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on"]
        unique_together = ("walletBox", "currency")

    # def __str__(self):
    #     return f"{self.walletBox.user.get_full_name()}-wallet"


class Entry(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for each user wallet",
    )
    currency = models.CharField(max_length=255)
    wallet = models.ForeignKey(
        "wallet.Wallets", on_delete=models.SET_NULL, null=True, related_name="entries"
    )
    wallet_available = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    wallet_balance = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    type = models.CharField(max_length=255)
    description = models.CharField(max_length=500,  null=True, default="Wallet Entry")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(choices=wallet_enums.WALLET_ENTRY_STATUS, max_length=50, default="PENDING") # bring this guy back to pending (default)
    reference = models.CharField(unique=True, max_length=1024)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_on']
    
    def __str__(self):
        return f"{self.wallet.walletBox.user.get_full_name()}-{self.created_on}-walletEntry"


class UserWalletBox(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for user multiple virtual wallets",
    )
    user = models.EmailField(
        max_length=256, unique=True, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    #
    withdrawable = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_on"]

    def credit(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr) -> Union[bool, Dict]: #added desc
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )
        try:
            Entry.objects.create(
                type="CREDIT",
                reference=ref,
                wallet_available=wallet.available + Decimal(amount),
                wallet_balance=wallet.balance + Decimal(amount),
                amount=amount,
                currency=currency,
                wallet=wallet,
                description=desc,
                status=status
            )
            wallet.available += Decimal(amount)
            wallet.balance += Decimal(amount)
            wallet.save()
            # wallet.trigger_related_event(ref, currency)
            return True, "successful"
        except IntegrityError:
            return False, "failed, reference already exits"
    
    def credit_balance(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr) -> Union[bool, Dict]:
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )
        try:
            Entry.objects.create(
                type="CREDIT",
                reference=ref,
                amount=amount,
                wallet_available=wallet.available,
                wallet_balance=wallet.balance + Decimal(amount),
                currency=currency,
                wallet=wallet,
                description=desc,
                status=status
            )
            wallet.balance += Decimal(amount)
            wallet.save()
            # wallet.trigger_related_event(ref, currency)
            return True, "successful"
        except IntegrityError:
            return False, "failed, reference already exits"

    def credit_available(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr) -> Union[bool, Dict]:
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )
        if round(float(float(wallet.available) + float(amount)), 2) > round(float(wallet.balance), 2):
            return False, "available cannot be greater than balance"
        try:
            Entry.objects.create(
                type="CREDIT",
                reference=ref,
                amount=amount,
                wallet_available=wallet.available + Decimal(amount),
                wallet_balance=wallet.balance,
                currency=currency,
                wallet=wallet,
                description=desc,
                status=status
            )
            wallet.available += Decimal(amount)
            wallet.save()
            # wallet.trigger_related_event(ref, currency)
            return True, "successful"
        except IntegrityError:
            return False, "failed, reference already exits"
    
    
    def debit(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr) -> Union[bool, Dict,]:
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )
        if wallet.available >= amount and wallet.balance >= amount:
            try:
                Entry.objects.create(
                    type="DEBIT",
                    reference=ref,
                    amount=amount,
                    wallet_available=wallet.available - Decimal(amount),
                    wallet_balance=wallet.balance - Decimal(amount),
                    currency=currency,
                    wallet=wallet,
                    description=desc,
                    status=status

                )
                wallet.available -= Decimal(amount)
                wallet.balance -= Decimal(amount)
                # wallet.trigger_related_event(ref, currency)
                wallet.save()
                return True, "successful"
            except IntegrityError:
                return False, "failed, reference already exits"
        else:
            return False, "failed,insufficient avaliable balance"
    

    def debit_available(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr) -> Union[bool, Dict,]:
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )
        if wallet.available >= amount:
            try:
                Entry.objects.create(
                    type="DEBIT",
                    reference=ref,
                    amount=amount,
                    wallet_available=wallet.available - Decimal(amount),
                    wallet_balance=wallet.balance,
                    currency=currency,
                    wallet=wallet,
                    description=desc,
                    status=status

                )
                wallet.available -= Decimal(amount)
                # wallet.trigger_related_event(ref, currency)
                wallet.save()
                return True, "successful"
            except IntegrityError:
                return False, "failed, reference already exits"

        else:
            return False, "failed,insufficient avaliable balance"
    
    def debit_balance(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr) -> Union[bool, Dict,]:
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )
        if wallet.balance >= amount:
            try:
                Entry.objects.create(
                    type="DEBIT",
                    reference=ref,
                    amount=amount,
                    wallet_available=wallet.available,
                    wallet_balance=wallet.balance - Decimal(amount),
                    currency=currency,
                    wallet=wallet,
                    description=desc,
                    status=status

                )
                # wallet.available -= Decimal(amount)
                wallet.balance -= Decimal(amount)
                # wallet.trigger_related_event(ref, currency)
                wallet.save()
                return True, "successful"
            except IntegrityError:
                return False, "failed, reference already exits"

        else:
            return False, "failed,insufficient avaliable balance"

    def balance_wallet_avalilable(self, currency: AnyStr, ref: AnyStr, desc: AnyStr, status: AnyStr):

        # get the wallet with the currency
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )

        # get the wallet available and balance
        wallet_available = wallet.available
        wallet_balance = wallet.balance

        # get the amount to be credited into the wallet available
        credit_amount = float(wallet_balance) - float(wallet_available)

        # credit the user's available
        is_credited, credit = self.credit_available(currency, credit_amount, ref, desc, status)
        if not is_credited:
            return False, credit
        
        return True, "Successfully balanced user wallet"
    
    def manual_entry_available_credit(self, currency: AnyStr, amount: float, ref: AnyStr, desc: AnyStr, status: AnyStr):

        # get the wallet with the currency
        wallet: Wallets

        wallet, is_created = Wallets.objects.get_or_create(
            currency=currency, walletBox_id=self.id
        )

        # get the wallet available and balance
        wallet_available = wallet.available
        wallet_balance = wallet.balance

        # confirm credit amount is not greater than balance
        credit_amount = round(float(wallet_available) + amount, 2)
        if credit_amount > float(wallet_balance):
            return False, "Wallet available amount cannot be greater than wallet balance amount"
        else:
        
            # credit the wallet available
            is_credited, credit = self.credit_available(currency, amount, ref, desc, status)
            if not is_credited:
                return False, credit
            
            return True, "Successfully credited user wallet available"

    def __str__(self):
        return f"{self.user.get_full_name()}_{self.id}"
        # return f"{self.user.get_full_name()}-{self.created_on}-walletBox"


class UserBankAccount(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for User bank accounts",
    )
    wallet = models.ForeignKey(
        Wallets, related_name="bank_accounts", on_delete=models.SET_NULL, null=True, blank=True
    )
    account_details = models.JSONField(default=dict)
    bank = models.CharField(max_length=50, help_text="Name of bank")
    alias = models.CharField(
        max_length=50, blank=True, null=True, help_text="short name of bank"
    )
    account_number = models.CharField(
        max_length=30, help_text="Bank account number", default=""
    )
    
    is_default = models.BooleanField(
        default=False, help_text="Is this your default bank account?"
    )
    is_verified = models.BooleanField(
        default=False, help_text="Is this your bank account verified?"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.wallet.walletBox.user.get_full_name()} - {self.alias.upper()}"

    class Meta:
        ordering = ["-created_on"]


class UserWalletWithdrawalRequest(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for Wallet withdrawals",
    )
    account = models.ForeignKey(
        UserBankAccount,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Bank account funds are transferred to",
    )
    amount = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, help_text="Withdrawal amount"
    )
    is_accepted = models.BooleanField(default=False)
    description = models.TextField(
        max_length=250, blank=True, null=True, help_text="Withdrawal description"
    )
    reference = models.CharField(max_length=254, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on"]

    def approve_withrawal_request(self):
        self.is_accepted = True
        self.save()
        return True


class UserWalletPinModel(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for Wallet Transaction pin",
    )

    user = models.EmailField(
        max_length=256, unique=True, null=False, blank=False)

    cypher_dict = models.JSONField(max_length=100, help_text="User wallet cypher", default=dict) 
    pin = models.CharField(max_length=100, help_text="User wallet pin", default='') 

    reset_code = models.CharField(max_length=100, help_text="User wallet reset code", default='') ###
   
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
