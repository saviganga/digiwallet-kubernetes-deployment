import django.conf as conf
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from user import models as user_models
from xauth import serializers as xauth_serializers
from xauth import utils as xauth_utils
from xauth import exceptions as xauth_exceptions
import django.conf as conf

from xauth.responses import xauth_responses

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from xauth import models as xauth_models
from django.utils import timezone
import datetime

class JWTAuth(APIView):

    @ swagger_auto_schema(
    request_body= xauth_serializers.JWTAuthSerializer,
    responses={
        201: xauth_serializers.JWTAuthSerializer(many=False)},
    )
    
    @permission_classes((AllowAny,))
    def post(self, request, *args, **kwargs):

        platform = request.headers.get('platform')
        if platform not in ['WEB', 'IOS', 'ANDROID', 'API']:
            print('login platform error')
            return Response(data={"status": "FAILED", "message": "Please pass the platform in your header"}, status=status.HTTP_400_BAD_REQUEST)

        serialized_data = xauth_serializers.JWTAuthSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)

        try:
            user = xauth_utils.find_user(
                serialized_data.validated_data.get("email", None),
                serialized_data.validated_data.get("username", None),
            )
        except Exception as e:
            print('excepton')
            print(e)
            return Response(data=xauth_responses.jwtautherror(), status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(serialized_data.validated_data.get("password")):

            token_db = xauth_models.AuthToken.objects.all()
            filter_now = {"user":f"{user.id}", "platform":f"{platform}"}
            exist_token = token_db.filter(**filter_now)
            if len(exist_token) == 0:
                if platform in ['IOS', 'ANDROID', 'API']:
                    jwt_token = xauth_utils.encode_jwt(user, hours=72, platform=platform)
                else:
                    jwt_token = xauth_utils.encode_jwt(user, hours=2, platform=platform)            
            else:
                curr_token = exist_token[0]
                if curr_token.expiry_date >= timezone.now() and platform in [ 'IOS', 'ANDROID', 'API']:
                    curr_token.expiry_date =  timezone.now() + datetime.timedelta(hours=72)
                    curr_token.save()
                    jwt_token = xauth_utils.regenerate_jwt(user=user, hours=72, platform=platform, token=curr_token.token)

                if curr_token.expiry_date < timezone.now() and platform in [ 'IOS', 'ANDROID', 'API']:
                    curr_token.delete()
                    jwt_token = xauth_utils.encode_jwt(user, hours=72, platform=platform)


                if curr_token.expiry_date >= timezone.now() and platform=='WEB':
                    curr_token.expiry_date =  timezone.now() + datetime.timedelta(hours=2)
                    curr_token.save()
                    jwt_token = xauth_utils.regenerate_jwt(user=user, hours=72, platform=platform, token=curr_token.token)

                if curr_token.expiry_date < timezone.now() and platform=='WEB':
                    curr_token.delete()
                    jwt_token = xauth_utils.encode_jwt(user, hours=2, platform=platform)

            return Response(
                data=xauth_responses.jwtauthsuccess(jwt_token),
                status=status.HTTP_200_OK
            )
        else:
            print('pw')
            return Response(data=xauth_responses.jwtautherror(), status=status.HTTP_401_UNAUTHORIZED)


class JWTDestroy(APIView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.META.get("HTTP_AUTHORIZATION", "")
        try:
            xauth_utils.destroy_jwt(
                jwt_token.split(" ", 1)[1], bool(request.query_params.get("all", None))
            )
        except Exception as e:
            data ={
                "status": "FAILED",
                "message": "User already logged out"
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        data ={
            "status": "SUCCESS",
            "message": "Logout successful"
        }
        return Response(data=data, status=status.HTTP_200_OK)
