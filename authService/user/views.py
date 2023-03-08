from ast import Try
from crypt import methods
from http.client import responses
from lib2to3.pgen2.pgen import DFAState
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from user.utilities import activation_token
from cloudtask import tasks

from xauth import connectdbs as connect_dbs



from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError


from xauth import utils as xauth_utils
from user import serializers as user_serializers
from user import models as user_models
from user.responses import u_responses
from user import enums as user_enums

from drf_yasg.utils import swagger_auto_schema
import copy
import time
from rest_framework import generics

from django_filters import rest_framework as filters
import random
import string

import hashlib
import os
import requests
import json

from   datetime import  datetime as dt, date
import pytz

from user import enums as user_enums


class GetEnums(APIView):

    def get(self, request):

        gender = user_enums.GENDER
        return Response(
            data={
                "status": "SUCCESS",
                "message": "Motherfucker",
                "data": gender
            },
            status=status.HTTP_200_OK
        )




class UserViewSet(ModelViewSet):
    queryset = user_models.CustomUser.objects.all()
    serializer_class = user_serializers.ReadCustomUserSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            return self.queryset.none()
        if self.request.user.is_staff and 'admin' in self.request.headers:
            return self.queryset.all()
        return self.queryset.filter(email=self.request.user.email)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            serializer = self.get_serializer(queryset, many=True)

            data = {
                "message": "Successfully users",
                "status": "SUCCESS",
                "data": serializer.data,
            }
            return Response(data)
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Unauthenticated User"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data

            context = {
                "status": "SUCCESS",
                "message": "Successfully fetched user",
                "data": data
            }

            return Response(context, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to perform this action"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], name="signup")
    @swagger_auto_schema(
        request_body=user_serializers.RegisterCustomUserSerializer,
        responses={
            201: user_serializers.RegisterUserResponseSerializer(many=False)},
    )
    def signup(self, request, *args, **kwargs):
        req = user_serializers.RegisterCustomUserSerializer(data=request.data)
        try:
            req.is_valid(raise_exception=True)
            user = req.save()

            supported_country_code = req.validated_data.get('supported_country')

            is_found, supported_country = connect_dbs.connect.validate_country(supported_country_code)
            if not is_found:
                data = {
                    "status": "FAILED",
                    "message": "invalid country",
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            access_token = xauth_utils.encode_jwt(user, hours=2,)

            return_serializer = user_serializers.RegisterUserResponseSerializer(
                data={"access": access_token}
            )
            return_serializer.is_valid(raise_exception=True)

            try:
                tasks.create_user_wallet_signup.delay(
                    user.email,
                    access_token,
                    "NGN"
                )
            except Exception as ea:
                print(ea)
                pass

            return Response(
                data=u_responses.user_created_success(return_serializer.data),
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(e)
            return Response(
                data=u_responses.create_user_error(req.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            user = self.get_object()
            user_copy = copy.deepcopy(user)
            serializer = user_serializers.UpdateCustomUserSerializer(
                user, data=request.data, partial=partial
            )
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if request.data.get("username") != user_copy.user_name:
                    # send otp to confirm new number
                    pass

                if request.data.get("email") != user_copy.email:
                    # send email to confirm email
                    pass

                return Response(
                    data=u_responses.user_update_success(serializer.data),
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                print(e)
                return Response(
                    data=u_responses.user_update_error(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to perform this action"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(request_body=user_serializers.ForgotPasswordSerializer)
    def change_password(self, request, pk=None):
        try:
            user = self.get_object()
            serializer = user_serializers.ChangePasswordSerializer(
                data=request.data)
            try:
                serializer.is_valid(raise_exception=True)

                if not user.check_password(
                        serializer.validated_data.get("old_password")
                ):
                    return Response(
                        data=u_responses.incorrect_password_error(),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # check if old password is same as new one  (check for optimization)
                if serializer.validated_data.get(
                        "old_password"
                ) == serializer.validated_data.get("password"):
                    return Response(
                        data=u_responses.password_and_oldpasswordmismatch(),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # check new passwords are the same
                if serializer.validated_data.get(
                        "password"
                ) != serializer.validated_data.get("re_password"):
                    return Response(
                        data=u_responses.password_and_confirmpassword_mismatch(),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user.set_password(serializer.validated_data["password"])
                user.save()
                return Response(
                    data=u_responses.password_change_success(), status=status.HTTP_200_OK
                )
            except Exception as e:
                print(e)
                return Response(
                    data=u_responses.change_password_error(serializer.errors),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to perform this action"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=["post"])
    @swagger_auto_schema(request_body=user_serializers.ForgotPasswordSerializer)
    def forgotpassword(self, request, *args, **kwargs):
        serializer = user_serializers.ForgotPasswordSerializer(
            data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            callback_url = request.query_params.get('callback')
            email = serializer.validated_data.get('email')
            try:
                user = user_models.CustomUser.objects.get(email=email)
            except Exception as e:
                print(e)
                return Response(
                    data=u_responses.user_does_not_exist_error(),
                    status=status.HTTP_400_BAD_REQUEST
                )

            # SEND EMAIL TO USER WITH RESET EMAIL LINK (password reset link/activation link)

            # move to method in models
            uid64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            tokenn = activation_token.make_token(user)
            reseturl = f'{callback_url}/auth/reset-password/?pk={uid64}&token={tokenn}'

            # send email for forgot password
            
            return Response(
                data={
                    "status": 'SUCCESS',
                    "message": "Password Reset Link has been sent to your email"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                data=u_responses.forgot_password_error(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    @swagger_auto_schema(request_body=user_serializers.ResetPasswordSerializer)
    def resetforgotpassword(self, request, *args, **kwargs):
        uid64 = request.query_params.get('pk')
        token = request.query_params.get('token')

        # VALIDATE ACTIVATION LINK
        # move to methods in models
        try:
            user_id = force_text(urlsafe_base64_decode(uid64))
        except Exception as e:
            print(e)
            return Response(data='bad')
        try:
            user = user_models.CustomUser.objects.get(pk=user_id)
        except Exception as e:
            print(e)
            return Response(
                data=u_responses.user_does_not_exist_error(),
                status=status.HTTP_400_BAD_REQUEST
            )
        if not activation_token.check_token(user, token):
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Invalid Password Reset Token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = user_serializers.ResetPasswordSerializer(
            data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

            password = serializer.validated_data.get('password')
            re_password = serializer.validated_data.get('re_password')

            if password != re_password:
                return Response(
                    data=u_responses.password_and_confirmpassword_mismatch(),
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(password)
            user.save()

            return Response(
                data={
                    "status": 'SUCCESS',
                    "message": "Password Successfully reset"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": 'FAILED',
                    "message": "Please check fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def staffusers(self, request, pk=None):
        queryset = self.queryset.filter(is_staff=True)
        
        serializer = self.serializer_class(queryset, many=True)
        return Response(
            data={
                "status": "SUCCESS",
                "message": "Successfully fetched staff users",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )