# from rest_framework.views import APIView
import os
import uuid
from django.urls import reverse
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from wallet import models as wallets_models
from wallet import serializers as wallet_serializer
from wallet import responses as wallet_responses
from wallet import enums as wallet_enums
from wallet import permissions as wallet_permissions


from decimal import Decimal
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

###
from django.utils import timezone
from xauth import utils as xauth_utils


####
from datetime import datetime, timedelta

###
import time
from rest_framework.permissions import AllowAny
from wallet import permissions as wallet_permissions

from wallet.conversion import ConversionProvider

from integrations.openpayd import PayD



class WalletsBox(ModelViewSet):

    # permission_classes = [wallet_permissions.UserWalletBoxPermissions |
                        #   wallet_permissions.AdminWalletBoxPermissions]
    queryset = wallets_models.UserWalletBox.objects.all()
    serializer_class = wallet_serializer.WalletBoxSerializer
    # read_serializer_class = wallet_serializer.ReadWalletBoxSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = wallet_filters.WalletBoxFilter

    def get_queryset(self): 
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()  
        is_user,user = xauth_utils.connect.validate_token(self.request.headers.get('authorization'))
        if 'admin' in self.request.headers and user.is_staff:
            return self.queryset.all() 
        return self.queryset.filter(user=user.email) 

    def create(self, request, *args, **kwargs):  
             
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data.get('user')
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                data={
                    "status": "SUCCESS",
                    "message": "Walletbox Successfully created",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Unable to create walletbox Please check fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            serializer = wallet_serializer.ReadWalletBoxSerializer(queryset, many=True)
            return Response(
                data=wallet_responses.WalletBoxResponses().get_wallets_success(
                    serializer.data
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to view this page"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    @swagger_auto_schema(
        request_body=wallet_serializer.WalletTransferSerializer,
    )
    @action(detail=False, methods=["post"])
    def transfer(self, request, *args, **kwargs):
        is_user,user = xauth_utils.connect.validate_token(request.headers.get('authorization'))
        first_name = user.first_name[::-3].upper()
        transfer_date = timezone.now().strftime("%m%d%Y%H%M%S")
        if request.data.get('reference') is None:
            request.data['reference'] = f"{first_name}{transfer_date}"
        serializer = wallet_serializer.WalletTransferSerializer(
            data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            sender_walletbox = wallets_models.UserWalletBox.objects.get(
                    user=user.email)
            try:
                receiver_walletbox = wallets_models.UserWalletBox.objects.get(
                    user=serializer.validated_data['receiver'])
            except Exception as e:
                print(e)
                return Response(data={"status": "FAILED", "message": "Receiver wallet box not found"}, status=status.HTTP_400_BAD_REQUEST)
            if sender_walletbox == receiver_walletbox:
                return Response(data={"status": "FAILED", "message": "Oops! You cannot transfer to your wallet"}, status=status.HTTP_400_BAD_REQUEST)

            is_debited, debit_status = sender_walletbox.debit(
                currency=serializer.validated_data.get('currency'),
                amount=serializer.validated_data.get('amount'),
                ref=f"WALLET-TX-DR-{serializer.validated_data.get('reference')}",
                desc=f"Wallet transfer WALLET-TX-DR-{serializer.validated_data.get('reference')} debit",
                status="SUCCESS"
            )
            if not is_debited:
                return Response(data={"status": "FAILED", "message": debit_status}, status=status.HTTP_400_BAD_REQUEST)

            is_credited, credit_status = receiver_walletbox.credit(
                currency=serializer.validated_data.get('currency'),
                amount=serializer.validated_data.get('amount'),
                ref=f"WALLET-TX-CR-{serializer.validated_data.get('reference')}",
                desc=f"Wallet transfer WALLET-TX-CR-{serializer.validated_data.get('reference')} credit",
                status="SUCCESS"
            )
            if not is_credited:
                return Response(data={"status": "FAILED", "message": credit_status}, status=status.HTTP_400_BAD_REQUEST)

            return Response(data={"status": "SUCCESS", "message": "Transfer Successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data={"status": "FAILED", "message": "Transfer Failed. Please Check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=["post"])
    def inter_currency_transfer(self, request, *args, **kwargs):
        is_user,user = xauth_utils.connect.validate_token(request.headers.get('authorization'))
        first_name = user.first_name[::-3].upper()
        transfer_date = timezone.now().strftime("%m%d%Y%H%M%S")
        if request.data.get('reference') is None:
            request.data['reference'] = f"{first_name}{transfer_date}"
        serializer = wallet_serializer.InterCurrencyTransfer(
            data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            sender_walletbox = wallets_models.UserWalletBox.objects.get(
                    user=user.email)
            try:
                receiver_walletbox = wallets_models.UserWalletBox.objects.get(
                    user=serializer.validated_data['receiver'])
            except Exception as e:
                print(e)
                return Response(data={"status": "FAILED", "message": "Receiver wallet box not found"}, status=status.HTTP_400_BAD_REQUEST)
            if sender_walletbox == receiver_walletbox:
                return Response(data={"status": "FAILED", "message": "Oops! You cannot transfer to your wallet"}, status=status.HTTP_400_BAD_REQUEST)
            
            conversion_provider = ConversionProvider()
            
            is_converted, converted = conversion_provider.convert(
                serializer.validated_data.get('from_currency'),
                serializer.validated_data.get('to_currency'),
                serializer.validated_data.get('amount'),
            )

            if not is_converted:
                print(converted)
                return Response(
                    data={
                        "status": "FAILED",
                        "data": converted
                    }
                )
            
            is_debited, debit_status = sender_walletbox.debit(
                currency=serializer.validated_data.get('from_currency'),
                amount=serializer.validated_data.get('amount'),
                ref=f"WALLET-TX-DR-{serializer.validated_data.get('reference')}",
                desc=f"Wallet transfer WALLET-TX-DR-{serializer.validated_data.get('reference')} debit",
                status="SUCCESS"
            )
            if not is_debited:
                return Response(data={"status": "FAILED", "message": debit_status}, status=status.HTTP_400_BAD_REQUEST)

            is_credited, credit_status = receiver_walletbox.credit(
                currency=serializer.validated_data.get('to_currency'),
                amount=Decimal(converted),
                ref=f"WALLET-TX-CR-{serializer.validated_data.get('reference')}",
                desc=f"Wallet transfer WALLET-TX-CR-{serializer.validated_data.get('reference')} credit",
                status="SUCCESS"
            )
            if not is_credited:
                return Response(data={"status": "FAILED", "message": credit_status}, status=status.HTTP_400_BAD_REQUEST)

            return Response(data={"status": "SUCCESS", "message": "Transfer Successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data={"status": "FAILED", "message": "Transfer Failed. Please Check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def stats(self, request, *args, **kwargs):
        
        payd = PayD()
        auth = payd.get_auth()

        # return_data = {
        #     "all_wallets": all_wallets
        # }

        return Response(
            data={
                "status": "SUCCESS",
                "message": "Successfully fetched stats",
                "data": auth
            },
            status=status.HTTP_200_OK
        )
            



    @swagger_auto_schema(
        request_body=wallet_serializer.WalletManualEntrySerializer,
    )
    @action(detail=False, methods=["post"])
    def manual_entry(self, request, *args, **kwargs):
        is_user,user = xauth_utils.connect.validate_token(request.headers.get('authorization'))
        first_name = user.first_name[::-3].upper()
        entry_date = timezone.now().strftime("%m%d%Y%H%M%S")
        jwt = request.headers.get('authorization').split(' ')
        jwt_token = jwt[1]
        if request.data.get('reference') is None:
            request.data['reference'] = f"{first_name}{entry_date}"

        try:
            serializer = wallet_serializer.WalletManualEntrySerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                try:
                    user_walletbox = wallets_models.UserWalletBox.objects.get(
                        user=serializer.validated_data.get('user'))
                except Exception as e:
                    print(e)
                    return Response(data={"status": "FAILED", "message": "WalletBox does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    platform_walletbox = wallets_models.UserWalletBox.objects.get(
                        user='visopay@gmail.com'
                    )
                except Exception as e:
                    print(e)
                    return Response(data={"status": "FAILED", "message": "Platform WalletBox does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                if serializer.validated_data.get('entry_type') not in wallet_enums.ENTRY_TYPE:
                    return Response(data={"status": "FAILED", "message": "Invalid Entry Type. Please try again"}, status=status.HTTP_400_BAD_REQUEST)

                if serializer.validated_data.get('entry_type') == 'DEBIT':
                    is_debited, debit_status = user_walletbox.debit(
                        currency=serializer.validated_data.get('currency'),
                        amount=serializer.validated_data.get('amount'),
                        ref=f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-DEBIT",
                        desc=serializer.validated_data.get('description'),
                        status="SUCCESS"
                    )

                    if not is_debited:
                        return Response(data={"status": "FAILED", "message": debit_status}, status=status.HTTP_400_BAD_REQUEST)

                    # credit platform wallet
                    is_platform_credited, platform_credited = platform_walletbox.credit(
                        currency=serializer.validated_data.get('currency'),
                        amount=serializer.validated_data.get('amount'),
                        ref=f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-CREDIT",
                        desc=serializer.validated_data.get('description'),
                        status="SUCCESS"
                    )

                    if not is_platform_credited:
                        return Response(data={"status": "FAILED", "message": platform_credited}, status=status.HTTP_400_BAD_REQUEST)

                    # send debit notifications here
                    ###

                    return Response(data={"status": "SUCCESS", "message": "DEBIT Entry Successfull"}, status=status.HTTP_200_OK)

                if serializer.validated_data.get('entry_type') == 'CREDIT':

                    is_platform_debited, platform_debited = platform_walletbox.debit(
                        currency=serializer.validated_data.get('currency'),
                        amount=serializer.validated_data.get('amount'),
                        ref=f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-DEBIT",
                        desc=serializer.validated_data.get('description'),
                        status="SUCCESS"
                    )
                    if not is_platform_debited:
                        return Response(data={"status": "FAILED", "message": platform_debited}, status=status.HTTP_400_BAD_REQUEST)

                    is_credited, credit_status = user_walletbox.credit(
                        currency=serializer.validated_data.get('currency'),
                        amount=serializer.validated_data.get('amount'),
                        ref=f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-CREDIT",
                        desc=serializer.validated_data.get('description'),
                        status="SUCCESS"
                    )

                    if not is_credited:
                        return Response(data={"status": "FAILED", "message": credit_status}, status=status.HTTP_400_BAD_REQUEST)

                    # send credit notifications here
                    ###
                    return Response(data={"status": "SUCCESS", "message": "Manual Entry Successfull"}, status=status.HTTP_200_OK)

            except Exception as e:
                print(e)
                return Response(data={"status": "FAILED", "message": "Entry Unsuccessful. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                print(e)
                return Response(data={"status": "FAILED", "message": "Entry Unsuccessful. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["post"])
    # def manual_entry_tx(self, request, *args, **kwargs):

    #     first_name = request.user.first_name[::-3].upper()
    #     entry_date = timezone.now().strftime("%m%d%Y%H%M%S")
    #     jwt = request.headers.get('authorization').split(' ')
    #     jwt_token = jwt[1]
    #     if request.data.get('reference') is None:
    #         request.data['reference'] = f"{first_name}{entry_date}"

    #     # to make a change here
    #     # if credit operation reconstruct rference as it is
    #     # if debit operation demand a trip ref.

    #     try:
    #         serializer = wallet_serializer.TXWalletManualEntrySerializer(data=request.data)
    #         try:
    #             serializer.is_valid(raise_exception=True)
    #             if serializer.validated_data.get('entry_type') not in wallet_enums.ENTRY_TYPE:
    #                 return Response(data={"status": "FAILED", "message": "Invalid Entry Type. Please try again"}, status=status.HTTP_400_BAD_REQUEST)

    #             if serializer.validated_data.get('entry_type') == 'DEBIT':
    #                 is_debited, debit_status = platform_walletbox.debit(
    #                     currency=serializer.validated_data.get('currency'),
    #                     amount=serializer.validated_data.get('amount'),
    #                     ref=f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-DEBIT",
    #                     desc=serializer.validated_data.get('description'),
    #                     status="SUCCESS"
    #                 )

    #                 if not is_debited:
    #                     return Response(data={"status": "FAILED", "message": debit_status}, status=status.HTTP_400_BAD_REQUEST)

    #                 return Response(data={"status": "SUCCESS", "message": "DEBIT Entry Successfull"}, status=status.HTTP_200_OK)

    #             if serializer.validated_data.get('entry_type') == 'CREDIT':

    #                 is_credited, credit_status = platform_walletbox.credit(
    #                     currency=serializer.validated_data.get('currency'),
    #                     amount=serializer.validated_data.get('amount'),
    #                     ref=f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-CREDIT",
    #                     desc=serializer.validated_data.get('description'),
    #                     status="SUCCESS"
    #                 )

    #                 if not is_credited:
    #                     return Response(data={"status": "FAILED", "message": credit_status}, status=status.HTTP_400_BAD_REQUEST)

    #                 # cloudtask
    #                 if os.environ.get('ENVIRONMENT') == 'STAGING':
    #                     try:
    #                         task_url = reverse("cloudtasks:activity-log-update")
    #                         payload = {
    #                             "description": f"{request.user.get_full_name()} performed a manual {serializer.validated_data.get('entry_type')}",
    #                             "category": "WALLET",
    #                             "jwt_token": jwt_token
    #                         }
    #                         send_task_staging(task_url, queue_name='activity-log-updates-queue-staging', payload=payload)
    #                     except Exception as gcp_cloudtask_error:
    #                         pass
    #                 else:
    #                     try:
    #                         task_url = reverse("cloudtasks:activity-log-update")
    #                         payload = {
    #                             "description": f"{request.user.get_full_name()} performed a manual {serializer.validated_data.get('entry_type')}",
    #                             "category": "WALLET",
    #                             "jwt_token": jwt_token
    #                         }
    #                         send_task(task_url, queue_name='activity-log-updates-queue', payload=payload)
    #                     except Exception as gcp_cloudtask_error:
    #                         pass

    #                 return Response(data={"status": "SUCCESS", "message": "Manual Entry Successfull"}, status=status.HTTP_200_OK)

    #         except Exception as e:
    #             print(e)
    #             return Response(data={"status": "FAILED", "message": "Entry Unsuccessful. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #             print(e)
    #             return Response(data={"status": "FAILED", "message": "Entry Unsuccessful. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    # @action(detail=False, methods=["post"])
    # def manual_entry_available(self, request, *args, **kwargs):
    #     first_name = request.user.first_name[::-3].upper()
    #     entry_date = timezone.now().strftime("%m%d%Y%H%M%S")
    #     jwt = request.headers.get('authorization').split(' ')
    #     jwt_token = jwt[1]
    #     if request.data.get('reference') is None:
    #         request.data['reference'] = f"{first_name}{entry_date}"

    #     try:
    #         serializer = wallet_serializer.WalletManualAvailableEntrySerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)

    #         # get the user's walletBox
    #         try:
    #             user_walletbox = wallets_models.UserWalletBox.objects.get(
    #                 user__email=serializer.validated_data.get('user'))
    #         except Exception as e:
    #             print(e)
    #             return Response(data={"status": "FAILED", "message": "WalletBox does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    #         # # set the reference 
    #         # ref = f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-CREDIT-AVAILABLE"

    #         # check if the request is to balance out the account
    #         if serializer.validated_data.get('balance_wallet') is True:
    #             # set the reference 
    #             ref = f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-CREDIT-AVAILABLE"

    #             # call the function to balance wallet available
    #             is_balanced, balance_available = user_walletbox.balance_wallet_avalilable(
    #                 serializer.validated_data.get('currency'),
    #                 ref,
    #                 serializer.validated_data.get('description'),
    #                 'SUCCESS'
    #                 )
                
    #             if not is_balanced:
    #                 return Response(data={"status": "FAILED", "message": balance_available}, status=status.HTTP_400_BAD_REQUEST)
                
    #             top_up_email = wallet_notifs.user_wallet_credit_email(
    #                     user_walletbox, serializer.validated_data.get('amount'), serializer.validated_data.get('currency'))

            
    #         else:
    #             # check if entry type is valid
    #             if serializer.validated_data.get('entry_type') not in wallet_enums.ENTRY_TYPE:
    #                 return Response(data={"status": "FAILED", "message": "Invalid Entry Type. Please try again"}, status=status.HTTP_400_BAD_REQUEST)

    #             # check if entry type is debit
    #             if serializer.validated_data.get('entry_type') == 'DEBIT':
    #                 # set the reference 
    #                 ref = f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-DEBIT-AVAILABLE"
    #                 is_debited, debit_status = user_walletbox.debit_available(
    #                     currency=serializer.validated_data.get('currency'),
    #                     amount=(serializer.validated_data.get('amount')),
    #                     ref=ref,
    #                     desc=serializer.validated_data.get('description'),
    #                     status="SUCCESS"
    #                 )

    #                 if not is_debited:
    #                     return Response(data={"status": "FAILED", "message": debit_status}, status=status.HTTP_400_BAD_REQUEST)
                    
    #                 debit_email = wallet_notifs.user_wallet_debit_email(
    #                     user_walletbox, serializer.validated_data.get('amount'), serializer.validated_data.get('currency'))


    #             # check if entry type is credit
    #             if serializer.validated_data.get('entry_type') == 'CREDIT':
    #                 # set the reference 
    #                 ref = f"WALLET-MANUAL-ENTRY-{serializer.validated_data.get('reference')}-CREDIT-AVAILABLE"
    #                 # call the function to perform manual entry available credit
    #                 is_credited, credit_status = user_walletbox.manual_entry_available_credit(
    #                     serializer.validated_data.get('currency'),
    #                     (serializer.validated_data.get('amount')),
    #                     ref,
    #                     serializer.validated_data.get('description'),
    #                     'SUCCESS'
    #                 )

    #                 if not is_credited:
    #                     return Response(data={"status": "FAILED", "message": credit_status}, status=status.HTTP_400_BAD_REQUEST)

    #                 top_up_email = wallet_notifs.user_wallet_credit_email(
    #                     user_walletbox, serializer.validated_data.get('amount'), serializer.validated_data.get('currency'))

    #         # cloudtask
    #         if os.environ.get('ENVIRONMENT') == 'STAGING':
    #             task_url = reverse("cloudtasks:activity-log-update")
    #             payload = {
    #                 "description": f"{request.user.get_full_name()} performed a manual {serializer.validated_data.get('entry_type')}",
    #                 "category": "WALLET",
    #                 "jwt_token": jwt_token
    #             }
    #             send_task_staging(task_url, queue_name='activity-log-updates-queue-staging', payload=payload)
                
    #         else:
    #             task_url = reverse("cloudtasks:activity-log-update")
    #             payload = {
    #                 "description": f"{request.user.get_full_name()} performed a manual {serializer.validated_data.get('entry_type')}",
    #                 "category": "WALLET",
    #                 "jwt_token": jwt_token
    #             }
    #             send_task(task_url, queue_name='activity-log-updates-queue', payload=payload)
                
    #         return Response(data={"status": "SUCCESS", "message": "Wallet available manual entry successfull"}, status=status.HTTP_200_OK)

    #     except Exception as serializer_exception:
    #         print(serializer_exception)
    #         return Response(data={"status": "FAILED", "message": "Entry Unsuccessful. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(
    #     request_body=wallet_serializer.UserWalletTopUpSerializer,
    # )
    # @action(detail=False, methods=["post"])
    # def topup(self, request, *args, **kwargs):
    #     first_name = request.user.first_name[::-3].upper()
    #     entry_date = timezone.now().strftime("%m%d%Y%H%M%S")
    #     if request.data.get('reference') is None:
    #         request.data['reference'] = f"{first_name}{entry_date}"
    #     serializer = wallet_serializer.UserWalletTopUpSerializer(
    #         data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
            
    #         try:
    #             user_walletbox = wallets_models.UserWalletBox.objects.get(
    #                 user=request.user)
    #         except Exception as e:
    #             print(e)
    #             return Response(data={"status": "FAILED", "message": "WalletBox does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    #         params = request.query_params.get('callback')

    #         # topup from paystack
    #         payment_provider = PaymentProvider()
    #         is_topup, topup = payment_provider.checkout(
    #             amount=serializer.validated_data.get('amount'),
    #             currency=serializer.validated_data.get('currency'),
    #             ref=f"WALLET-TOPUP_{serializer.validated_data.get('reference')}",
    #             email=request.user.email,
    #             success_url=params
    #         )
    #         if not is_topup:
    #             return Response(data={"status": "FAILED", "message": topup}, status=status.HTTP_400_BAD_REQUEST)

    #         # This is where to send top up notifications to user
    #         top_up_email = wallet_notifs.user_wallet_top_up_email(
    #             user_walletbox, serializer.validated_data.get('amount'))

    #         return Response(data={"status": "SUCCESS", "message": "Wallet TopUp Successful", "data": topup}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print(e)
    #         return Response(data={"status": "FAILED", "message": "Unable to TopUp Wallet. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["post"], permission_classes = [wallet_permissions.AdminWalletBoxPermissions | CustomOverridePermissions])
    #     jwt = request.headers.get('authorization').split(' ')
    #     jwt_token = jwt[1]
    #     first_name = request.user.first_name[::-3].upper()
    #     entry_date = timezone.now().strftime("%m%d%Y%H%M%S")
    #     if request.data.get('reference') is None:
    #         request.data['reference'] = f"{first_name}{entry_date}"
    #     serializer = wallet_serializer.UserWalletTopUpSerializer(
    #         data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #         try:
    #             user_walletbox = wallets_models.UserWalletBox.objects.get(
    #         except Exception as e:
    #             print(e)
    #             return Response(data={"status": "FAILED", "message": "WalletBox does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    #         params = request.query_params.get('callback')

    #         # topup from paystack
    #         payment_provider = PaymentProvider()
    #         is_topup, topup = payment_provider.checkout(
    #             amount=serializer.validated_data.get('amount'),
    #             currency=serializer.validated_data.get('currency'),
    #             email=request.user.email,
    #             success_url=params
    #         )
    #         if not is_topup:
    #             return Response(data={"status": "FAILED", "message": topup}, status=status.HTTP_400_BAD_REQUEST)


    #         # This is where to send top up notifications to user
    #         top_up_email = wallet_notifs.user_wallet_top_up_email(
    #             user_walletbox, serializer.validated_data.get('amount'))

    #         # cloudtask
    #         if os.environ.get('ENVIRONMENT') == 'STAGING':
    #             try:
    #                 task_url = reverse("cloudtasks:activity-log-update")
    #                 payload = {
    #                     "category": "RECORDS",
    #                     "jwt_token": jwt_token
    #                 }
    #                 send_task_staging(task_url, queue_name='activity-log-updates-queue-staging', payload=payload)
    #             except Exception as gcp_cloudtask_error:
    #                 pass
    #         else:
    #             try:
    #                 task_url = reverse("cloudtasks:activity-log-update")
    #                 payload = {
    #                     "category": "RECORDS",
    #                     "jwt_token": jwt_token
    #                 }
    #                 send_task(task_url, queue_name='activity-log-updates-queue', payload=payload)
    #             except Exception as gcp_cloudtask_error:
    #                 pass


    #     except Exception as e:
    #         print(e)
    #         return Response(data={"status": "FAILED", "message": "Unable to TopUp Wallet. Please check fields and try again", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["get"])
    # def stats(self, request, *args, **kwargs):

    #     all_walletboxes = self.queryset.all().count()

    #     return_data = {
    #         "all_walletboxes": all_walletboxes
    #     }

    #     return Response(
    #         data={
    #             "status": "SUCCESS",
    #             "message": "Successfully fetched stats",
    #             "data": return_data
    #         },
    #         status=status.HTTP_200_OK
    #     )

class Wallets(ModelViewSet):
    queryset = wallets_models.Wallets.objects.all()
    # permission_classes = [wallet_permissions.AdminWalletsPermissions | wallet_permissions.UserWalletsPermissions]
    
    serializer_class = wallet_serializer.WalletsSerializer
    
    def get_queryset(self): 
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()  
        is_user,user = xauth_utils.connect.validate_token(self.request.headers.get('authorization'))
        if 'admin' in self.request.headers and user.is_staff:
            return self.queryset.all() 
        return self.queryset.filter(walletBox__user=user.email) 

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            serializer = wallet_serializer.ReadWalletsSerializer(queryset, many=True)
            return Response(
                data=wallet_responses.WalletBoxResponses().get_wallets_success(
                    serializer.data
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to view this page"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            "message": "Successfully fetched wallet",
            "status": "SUCCESS",
            "data": serializer.data,
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        is_user, user = xauth_utils.connect.validate_token(request.headers.get('authorization'), email=True)
        

        try:
            # find currenvy
            is_currency, valid_currency = xauth_utils.connect.validate_currency(request.data.get('currency'))
            if not is_currency:
                return Response(
                    data={
                        "status": "FAILED",
                        "message": "Invalid currency"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as ex:
            print(ex)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Country does not exist",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                data={
                    "status": "SUCCESS",
                    "message": "Wallet Successfully created",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Unable to create wallet. Please check fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def stats(self, request, *args, **kwargs):

        all_wallets = self.queryset.all().count()

        return_data = {
            "all_wallets": all_wallets
        }

        return Response(
            data={
                "status": "SUCCESS",
                "message": "Successfully fetched stats",
                "data": return_data
            },
            status=status.HTTP_200_OK
        )

    

class Entry(ModelViewSet):
    permission_classes = [wallet_permissions.UserWalletEntriesPermissions | wallet_permissions.AdminWalletEntriesPermissions]
    queryset = wallets_models.Entry.objects.all()
    serializer_class = wallet_serializer.EntrySerializer
    

    def get_queryset(self): 
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()  
        is_user,user = xauth_utils.connect.validate_token(self.request.headers.get('authorization'))
        if 'admin' in self.request.headers and user.is_staff:
            return self.queryset.all() 
        return self.queryset.filter(wallet__walletBox__user=user.email) 


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        data = {"status": "SUCCESS",
                "message": "successful", "data": serializer.data}
        return Response(data=data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            "message": "Successfully fetched wallet",
            "status": "SUCCESS",
            "data": serializer.data,
        }
        return Response(data)

    @action(detail=False, methods=["get"])
    def stats(self, request, *args, **kwargs):

        all_entries = self.queryset.all().count()
        credit_entries = self.queryset.filter(type='CREDIT').count()
        debit_entries = self.queryset.filter(type='DEBIT').count()

        return_data = {
            "total_entries": all_entries,
            "all_credits": credit_entries,
            "all_debits": debit_entries
        }

        return Response(
            data={
                "status": "SUCCESS",
                "message": "Successfully fetched stats",
                "data": return_data
            },
            status=status.HTTP_200_OK
        )

class UserBankAccountView(ModelViewSet):
    queryset = wallets_models.UserBankAccount.objects.all()
    serializer_class = wallet_serializer.UserBankAccountSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        if self.request.user.is_staff and 'admin' in self.request.headers:
            return self.queryset.all()
        return self.queryset.filter(wallet__walletBox__user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            serializer = self.serializer_class(queryset, many=True)
            return Response(
                data={
                    "status": "SUCCESS",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to view this page"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def create(self, request, *args, **kwargs):

        # add account number
        if request.data.get('account_number') == None:
            request.data['account_number'] = request.data.get('account_details').get('account_number')
       
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data.get('wallet').country.currency == 'NGN':

                # check if bank account number exists with the wallet
                account = wallets_models.UserBankAccount.objects.filter(
                            wallet =serializer.validated_data.get('wallet'),
                            account_number=serializer.validated_data.get('account_details').get('account_number')
                            )

                if account.exists():
                    return Response(
                        data={
                            "status": "FAILED",
                            "message": "Bank account already added"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )


                # verify bank account
                payment_provider = PaymentProvider()
                is_verified, verified_account = payment_provider.verify_account_number(
                    serializer.validated_data.get('account_details').get('account_number'),
                    serializer.validated_data.get('account_details').get('bank_code')
                )
                if not is_verified:
                    return Response(data={"status": "FAILED", "message": "Invalid Bank Account. Please check account number and bank code", "data": verified_account}, status=status.HTTP_400_BAD_REQUEST)

                self.perform_create(serializer)

                return Response(
                    data={
                        "status": "SUCCESS",
                        "data": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    data={
                        "status": "FAILED",
                        "message": "Sorry, Bank accounts are not available for the selected region"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Unable to create User Bank Account. Please check fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # @action(detail=False, methods=["get"])
    # def valid_banks(self, request):

    #     currency = request.query_params.get('currency')
    #     if currency == 'NGN':
    #         payment_provider = PaymentProvider()

    #         is_true, valid_banks = payment_provider.get_valid_banks(currency)
    #         if not is_true:
    #             return Response(
    #                 data={
    #                     "status": "FAILED",
    #                     "data": valid_banks
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         return_data = valid_banks
    #         return Response(
    #             data={
    #                 "status": "SUCCESS",
    #                 "message": "Successfully retrieved banks",
    #                 "data": return_data
    #             },
    #             status=status.HTTP_200_OK
    #         )
    #     else:
    #         return Response(
    #             data={
    #                 "status": "SUCCESS",
    #                 "message": "Sorry, details for this currency are not available"
    #             }
    #         )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            "message": "Successfully fetched user account",
            "status": "SUCCESS",
            "data": serializer.data,
        }
        return Response(data)


    @action(detail=False, methods=["get"])
    def stats(self, request, *args, **kwargs):

        all_bank_accounts = self.queryset.all().count()

        return_data = {
            "all_bank_accounts": all_bank_accounts,
        }

        return Response(
            data={
                "status": "SUCCESS",
                "message": "Successfully fetched stats",
                "data": return_data
            },
            status=status.HTTP_200_OK
        )

# class UserWalletWithdrawal(ModelViewSet):
#     serializer_class = wallet_serializer.WithdrawSerializer
#     queryset = wallets_models.UserWalletWithdrawalRequest.objects.all()

#     def get_queryset(self):
#         if getattr(self, 'swagger_fake_view', False):
#             return self.queryset.none()
#         if self.request.user.is_staff and 'admin' in self.request.headers:
#             return self.queryset.all()
#         return self.queryset.filter(account__wallet__walletBox__user=self.request.user)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.serializer_class(queryset, many=True)
#         return Response(
#             data={
#                 "status": "SUCCESS",
#                 "data": serializer.data
#             },
#             status=status.HTTP_200_OK,
#         )

#     def create(self, request, *args, **kwargs):

#         first_name = request.user.first_name[::-3].upper()
#         withdrawal_date = timezone.now().strftime("%m%d%Y%H%M%S")
#         if request.data.get('reference') is None:
#             request.data['reference'] = f"{first_name}{withdrawal_date}"


#         serializer = self.serializer_class(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#             user_wallet = serializer.validated_data.get('account').wallet

#             # check is_withrawable
#             if not user_wallet.walletBox.withdrawable:
#                 return Response(
#                     data={
#                         "status":"FAILED",
#                         "message": "You cannot perform a withdrawal at this time.Please contact Admin to enable your withdrawal"   
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             if user_wallet.country.currency == 'NGN':
#                 payment_provider = PaymentProvider()

#                 # create a transfer recipient
#                 if serializer.validated_data.get('account').account_details.get('recipient_code') is None:
#                     is_created, transfer_recipient = payment_provider.create_transfer_recipient(
#                         serializer.validated_data.get('account').account_details.get('account_number'),
#                         serializer.validated_data.get('account').account_details.get('bank_code'),
#                         serializer.validated_data.get('account').wallet.country.currency)
#                     if not is_created:
#                         return Response(data={"status": "FAILED", "message": "Unable to create transfer recipient"}, status=status.HTTP_400_BAD_REQUEST)
#                     serializer.validated_data.get('account').account_details['recipient_code'] = transfer_recipient
#                     serializer.validated_data.get('account').save()

#                 amt = serializer.validated_data.get('amount')
#                 if user_wallet.available < amt:
#                     return Response(
#                         data={
#                             "status":"FAILED",
#                             "message": "Oops! Insufficient funds in wallet balance."
#                         },
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 # initiate transfer
#                 is_transferred, transfer = payment_provider.initiate_paystack_transfer(
#                     amt, serializer.validated_data.get('account').account_details.get('recipient_code')
#                 )
#                 if not is_transferred:
#                     return Response(data={"status": "FAILED", "message": transfer}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # debit the user's wallet
#                 user_wallet.walletBox.debit_available(
#                     serializer.validated_data.get('account').wallet.country.currency,
#                     float(amt),
#                     f"WALLET-WITHDRWAL-{serializer.validated_data.get('reference')}-AVAILABLE",
#                     f"Wallet withdrawal",
#                     "SUCCESS"
#                 )
                
#                 self.perform_create(serializer)

#                 # disable driver withdrawal after a successful withdrawal
#                 user_wallet_box = user_wallet.walletBox
#                 user_wallet_box.withdrawable = False
#                 user_wallet_box.save()

#                 return Response(
#                     data={
#                         "status": "SUCCESS",
#                         "message": "Wallet withdrawal successful",
#                         "data": transfer
#                     },
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "Sorry, we do not have a withdrawal feature for this currency yet"
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#         except Exception as e:
#             print(e)
#             return Response(data={"status": "FAILED", "message": "Unable to process withdrawal. Please check account number and bank code", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False, methods=["get"])
#     def stats(self, request, *args, **kwargs):

#         all_requests = self.queryset.all().count()

#         return_data = {
#             "all_requests": all_requests
#         }

#         return Response(
#             data={
#                 "status": "SUCCESS",
#                 "message": "Successfully fetched stats",
#                 "data": return_data
#             },
#             status=status.HTTP_200_OK
#         )

# class UserWalletPinView(ModelViewSet):
#     serializer_class = wallet_serializer.UserWalletPinSerializer
#     queryset = wallets_models.UserWalletPinModel.objects.all()

#     permission_classes = [wallet_permissions.AdminWithdrawalPermissions | wallet_permissions.UserWithdrawalPermissions]

#     def get_queryset(self):
#         if getattr(self, 'swagger_fake_view', False):
#             # queryset just for schema generation metadata
#             return self.queryset.none()
#         if self.request.user.is_staff and 'admin' in self.request.headers and self.request.query_params:
#             return self.queryset.all()
#         if self.request.user.is_staff and 'admin' in self.request.headers:
#             return self.queryset.all()
#         return self.queryset.filter(user=self.request.user)

#     def create(self, request, *args, **kwargs):

#         if not request.data.get('user'):
#             request.data['user'] = request.user.id

#         # check if user already existed

#         try:
#             wallets_models.UserWalletPinModel.objects.get(user=request.user)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": "User pin already exists.Reset pin if forgotten",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             print('user does not have a pin yet..proceed')
            
#         pin = request.data.pop('pin')
#         # decrypted_pin = PinChecker.wallet_pin_RSA_resolver(pin)
        
#         if os.environ.get('ENVIRONMENT') == "STAGING":
#             cypher_dict = AES256_service.encrypt(
#                 plain_text=pin,
#                 password=os.environ.get('WALLET_PIN_KEY_STAGING')
#             )

#         if os.environ.get('ENVIRONMENT') == "PRODUCTION":
#             cypher_dict =AES256_service.encrypt(
#                 plain_text=pin,
#                 password=os.environ.get('WALLET_PIN_KEY_PRODUCTION')
#             )

#         request.data['cypher_dict'] = cypher_dict
#         request.data['pin'] = cypher_dict.get('cipher_text')

#         serializer = self.serializer_class(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)

#             return Response(
#                 data={
#                     "status": "SUCCESS",
#                     "message": "Successfully created wallet pin"
#                 },
#                 status=status.HTTP_201_CREATED
#             )
#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": serializer.errors,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     @ action(detail=False, methods=["post"])
#     def validate(self, request, *args, **kwargs):

#         if not request.data.get('user'):
#             request.data['user'] = request.user.id


#         # check if user's pin  is in the enccrypted pin store
#         if not wallets_models.UserWalletPinModel.objects.filter(user=request.user).exists():
#             return Response(
#                     data={
#                         "status":"FAILED",
#                         "message": "Oops! Your first withdrawal please setup your pin first."
#                     },
#                     status=status.HTTP_400_BAD_REQUEST 
#                     # status=status.HTTP_205_RESET_CONTENT # change to 205 
#             )

#         serializer = wallet_serializer.ValidateUserWalletPinSerializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#             user = serializer.validated_data.get('user')

#             try:
#                 user_wallet_pin = wallets_models.UserWalletPinModel.objects.get(user=user)
#             except Exception as user_wallet_pin_error:
#                 print(user_wallet_pin_error)
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "Incorrect wallet pin. Not set"
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            

#             # check  decrypt RSA in transit 
#             is_pin, pin_msg = PinChecker.wallet_pin_resolver_checker(
#                 serializer.data.get('pin'),
#                 serializer.data.get('user')
#                 )
#             if not is_pin:
#                 return Response(
#                         data={
#                             "status":"FAILED",
#                             "message": pin_msg
#                         },
#                         status=status.HTTP_400_BAD_REQUEST
#                 )

#             ###
        
#             # encrypted_pin = user_wallet_pin.pin
#             # print(encrypted_pin)

#             # if os.environ.get('ENVIRONMENT') == "STAGING":
#             #     decrypted_pin = AES_service.decrypt(
#             #         key=os.environ.get("WALLET_PIN_KEY_STAGING"),
#             #         enc_key=encrypted_pin
#             #     )
#             # else:
#             #     decrypted_pin =AES_service.decrypt(
#             #         key=os.environ.get("WALLET_PIN_KEY_PRODUCTION"),
#             #         enc_key=encrypted_pin
#             #     )
            
#             # print(decrypted_pin)
            
#             # if decrypted_pin != serializer.validated_data.get('pin'):
#             #     return Response(
#             #         data={
#             #             "status": "FAILED",
#             #             "message": "Incorrect wallet pin"
#             #         },
#             #         status=status.HTTP_400_BAD_REQUEST
#             #     )
            

#             ###


#             return Response(
#                 data={
#                     "status": "SUCCESS",
#                     "message": "Wallet pin successfully validated"
#                 },
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": "Unable to validate wallet pin. Please check fields and try again",
#                     "data": serializer.errors
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#     @ action(detail=False, methods=["post"])
#     def encrypt_RSA(self, request, *args, **kwargs):
#         try:
#             serializer = wallet_serializer.PinSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)

#             try:
#                 cypher = rsa.encrypt(serializer.data.get('pin'))
#                 return Response(
#                     data={
#                         "status": "SUCCESS",
#                         "RSA-Encryption": cypher, 
#                     },
#                     status=status.HTTP_200_OK
#                 )
#             except Exception as e:
#                 print(e)
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "unable to encrypt",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
                

#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": serializer.errors,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     @ action(detail=False, methods=["post"])
#     def decrypt_RSA(self, request, *args, **kwargs):
#         try:
#             serializer = wallet_serializer.PinSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)


#             try:
#                 plain_text = rsa.decrypt(request.data['pin'])
#                 return Response(
#                     data={
#                         "status": "SUCCESS",
#                         "message": plain_text,
#                     },
#                     status=status.HTTP_200_OK
#                 )
#             except Exception as e:
#                 print(e)
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "unable to decrypt",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
                

#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": e
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )


#     @ action(detail=False, methods=["get"])
#     def request_reset_withdrawal_pin(self, request, *args, **kwargs):

#         try:
#             user_pin_DB = wallets_models.UserWalletPinModel.objects.get(user=request.user)
#             reset_code = wallet_utils.wallet_service.reset_code_genenerator()
#             user_pin_DB.reset_code = reset_code
#             user_pin_DB.save()

#             print(reset_code)
#             try:
#                 # wallet_notifs.user_withdrawal_reset_email(user_pin_DB)
#                 wallet_notifs.user_withdrawal_reset_sms(user_pin_DB)
#             except Exception as e:     
#                 print(e)
#                 return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": "cannot Send user reset code at this time. try again",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#                 )

#             return Response(
#                     data={
#                         "status": "SUCCESS",
#                         "message":"Successfully reset pin",
#                     },
#                     status=status.HTTP_200_OK
#                 )

#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": "User does not have a withdrawal pin",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
                
#     @ action(detail=False, methods=["post"])
#     def validate_withdrawal_reset_code(self, request, *args, **kwargs):
#         try:
#             serializer = wallet_serializer.PinValidateSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)

#             try:
#                 reset_code = wallets_models.UserWalletPinModel.objects.get(user=serializer.validated_data.get('user')).reset_code

#                 if serializer.validated_data.get('reset_code') == reset_code:
#                     return Response(
#                         data={
#                             "status": "SUCCESS",
#                             "message": "Wallet reset code validated",
#                         },
#                         status=status.HTTP_200_OK
#                     )
#                 if serializer.validated_data.get('reset_code')   != reset_code:
#                     return Response(
#                         data={
#                             "status": "FAILED",
#                             "message": "Invalid wallet reset code. Check your mail for reset code or reset password again",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except Exception as e:
#                 print(e)
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "User do not have awithdrawal pin",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
                

#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": e
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     @ action(detail=False, methods=["post"])
#     def reset_withdrawal_pin(self, request, *args, **kwargs):
#         try:
             
#             serializer = wallet_serializer.PinResetSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)

#             if serializer.validated_data.get('pin') != serializer.validated_data.get('confirm_pin'):
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "Pin don't match",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             try:
#                 user_pin_DB = wallets_models.UserWalletPinModel.objects.get(user=serializer.validated_data.get('user'))
#                 pin = serializer.validated_data.get('pin')

#                 if os.environ.get('ENVIRONMENT') == "STAGING":
#                     cypher_dict = AES256_service.encrypt(
#                     plain_text=pin,
#                     password=os.environ.get('WALLET_PIN_KEY_STAGING')
#                 )

#                 # print(cypher_dict, cypher_dict.get('cipher_text'))

#                 if os.environ.get('ENVIRONMENT') == "PRODUCTION":
#                     cypher_dict =AES256_service.encrypt(
#                     plain_text=pin,
#                     password=os.environ.get('WALLET_PIN_KEY_PRODUCTION')
#                 )


#                 user_pin_DB.cypher_dict = cypher_dict
#                 user_pin_DB.pin = cypher_dict.get('cipher_text')
#                 user_pin_DB.save()

#                 return Response(
#                         data={
#                             "status": "SUCCESS",
#                             "message": "Withdrawal pin reset successsful",
#                         },
#                         status=status.HTTP_200_OK
#                     )

#             except Exception as e:
#                 print(e)
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "User does not have a withdrawal pin",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#         except Exception as e:
#             print(e)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": "Invalid Details"
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     @ action(detail=False, methods=["post"])
#     def change_withdrawal_pin(self, request, *args, **kwargs):

#         serializer = wallet_serializer.ChangePinSerializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)

#             # validate the old pin
#             is_pin, pin_msg = PinChecker.wallet_pin_resolver_checker(
#                 serializer.validated_data.get('old_pin'),
#                 serializer.data.get('user')
#                 )

#             if not is_pin:
#                 return Response(
#                         data={
#                             "status":"FAILED",
#                             "message": 'Incorrect old pin'
#                         },
#                         status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # confirm new pin 
#             if serializer.validated_data.get('pin') != serializer.validated_data.get('confirm_pin'):
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "Pin and confirm pin do not match",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             try:
#                 user_pin_DB = wallets_models.UserWalletPinModel.objects.get(user=serializer.validated_data.get('user'))
#                 pin = serializer.validated_data.get('pin')

#                 if os.environ.get('ENVIRONMENT') == "STAGING":
#                     cypher_dict = AES256_service.encrypt(
#                     plain_text=pin,
#                     password=os.environ.get('WALLET_PIN_KEY_STAGING')
#                 )

#                 print(cypher_dict, cypher_dict.get('cipher_text'))

#                 if os.environ.get('ENVIRONMENT') == "PRODUCTION":
#                     cypher_dict =AES256_service.encrypt(
#                     plain_text=pin,
#                     password=os.environ.get('WALLET_PIN_KEY_PRODUCTION')
#                 )


#                 user_pin_DB.cypher_dict = cypher_dict
#                 user_pin_DB.pin = cypher_dict.get('cipher_text')
#                 user_pin_DB.save()
#                 return Response(
#                             data={
#                                 "status": "SUCCESS",
#                                 "message": "Withdrawal pin changed successsful",
#                             },
#                             status=status.HTTP_200_OK
#                         )

#             except Exception as e:
#                 print(e)
#                 return Response(
#                     data={
#                         "status": "FAILED",
#                         "message": "User does not have a withdrawal pin",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         except Exception as serializer_error:
#             print(serializer_error)
#             return Response(
#                 data={
#                     "status": "FAILED",
#                     "message": "Unable to change wallet in. Please check fields and try again",
#                     "data": serializer.errors
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
                
