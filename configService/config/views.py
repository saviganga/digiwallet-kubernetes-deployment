from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from config import models as config_models
from config import serializers as config_serializer
from config.responses import country_responses
from rest_framework import status, generics
from rest_framework.response import Response
from config import permissions as config_permissions
from xauth import utils as xauth_utils



# Create your views here.
class CountryViewSet(ModelViewSet):
    queryset = config_models.Country.objects.all()
    serializer_class = config_serializer.CountrySerializer
    permission_classes = [config_permissions.AdminPermissions]

    def get_queryset(self): 
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()  
        is_user,user = xauth_utils.connect.validate_token(self.request.headers.get('authorization'))
        if 'admin' in self.request.headers and user.is_staff:
            return self.queryset.all() 
        return self.queryset.none() #(user=user.email) 

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # queryset = config_models.Country.objects.all()
        serializer = config_serializer.CountrySerializer(
            queryset, many=True)
        return Response(data=country_responses.get_country_success(serializer.data), status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        print('view')
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(data=country_responses.create_country_success(serializer.data), status=status.HTTP_201_CREATED, headers=headers)
        except Exception:
            return Response(data=country_responses.create_country_error(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        country = self.get_object()
        serializer = config_serializer.CountrySerializer(
            country, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(data=country_responses.update_country_success(serializer.data), status=status.HTTP_200_OK)
        except Exception:
            return Response(data=country_responses.update_country_error(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class SupportedCountryViewSet(ModelViewSet):
    queryset = config_models.SupportedCountry.objects.all()
    serializer_class = config_serializer.SupportedCountry

    def list(self, request, *args, **kwargs):
        queryset = config_models.SupportedCountry.objects.all()
        serializer = config_serializer.ReadSupportedCountrySerializer(
            queryset, many=True)
        return Response(data=country_responses.get_supportedcountry_success(serializer.data), status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            is_created, supported_country = serializer.create(serializer.validated_data)
            if not is_created:
                return Response(
                    data={
                        "status": "FAILED",
                        "message": supported_country
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            headers = self.get_success_headers(serializer.data)
            return Response(data=country_responses.create_supportedcountry_success(supported_country), status=status.HTTP_201_CREATED, headers=headers)
        except Exception:
            return Response(data=country_responses.create_supportedcountry_error(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        supported_country = self.get_object()
        serializer = self.serializer_class(
            supported_country, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(data=country_responses.update_supportedcountry_success(serializer.data), status=status.HTTP_200_OK)
        except Exception:
            return Response(data=country_responses.update_supportedcountry_error(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

