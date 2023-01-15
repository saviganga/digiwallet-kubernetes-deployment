from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from user import models as user_models
from user.responses import u_responses

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from xauth import connectdbs as connect_dbs



class RegisterCustomUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(
        label=_("Repeat Password"),
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    supported_country = serializers.CharField(required=True)

    class Meta:
        model = user_models.CustomUser
        fields = [
            "id",
            "email",
            "user_name",
            "first_name",
            "last_name",
            "phone",
            "password",
            "re_password",
            "source",
            "supported_country",
        ]
        read_only_fields = ("is_active", "is_staff",)

        extra_kwargs = {

            "password": {
                "write_only": True
            },
            "error_messages": {
                "required": "The password field is required"
            },

            "last_name": {
                "error_messages": {
                    "required": "The last name field is required"
                }
            },

            "first_name": {
                "error_messages": {
                    "required": "The first name field is required"
                }
            },

            "email": {
                "error_messages": {
                    "required": "The email field is required"
                }
            },

            "phone": {
                "error_messages": {
                    "required": "The phone field is required"
                }
            },

            "source": {
                "error_messages": {
                    "required": "The source field is required"
                }
            },

            "supported_country": {
                "error_messages": {
                    "required": "The supported country field is required"
                }
            },

        }

    def create(self, validated_data):

        # validate password from validated data
        password = validated_data.pop("password")
        re_password = validated_data.pop("re_password")

        if password != re_password:
            msg = u_responses.password_mismatch_error()
            raise serializers.ValidationError(msg, code="Password Mismatch")
        
        supported_country_code = validated_data.get('supported_country')
        
        # FIND SUPPORTED COUNTRY

        
        # is_found, supported_country = connect_dbs.connect.validate_country(supported_country_code)
        # if not is_found:
        #     return False, supported_country
        
        # create the user
        user = user_models.CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UpdateCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "supported_country",
            "referral_code",
        ]


class ConfirmSocialRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    access = serializers.CharField(max_length=1500, required=True)

###
# for user delete
class DeleteUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)

class EnableUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class SocialRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=254, required=True, error_messages={
                                       "required": "The first name field is required", "blank": "The first name field cannot be blank"})
    user_name = serializers.CharField(max_length=254, required=True, error_messages={
                                       "required": "The user name field is required", "blank": "The user name field cannot be blank"})
    last_name = serializers.CharField(max_length=254, required=True, error_messages={
                                      "required": "The last name field is required", "blank": "The last name field cannot be blank"})
    email = serializers.EmailField(max_length=254, required=True, error_messages={
                                   "required": "The email field is required", "blank": "The email field cannot be blank"})
    phone = serializers.CharField(max_length=15, required=True, error_messages={
                                  "required": "The phone number field is required", "blank": "The phone number field cannot be blank"})
    source = serializers.CharField(max_length=50, required=True)
    supported_country = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={
                                   "required": "The email field is required", "blank": "The email field cannot be blank"})


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    re_password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=254, error_messages={
                                         "required": "The old password field is required", "blank": "The old password field cannot be blank"})
    password = serializers.CharField(required=True, max_length=254, error_messages={
                                     "required": "The new password field is required", "blank": "The new password field cannot be blank"})
    re_password = serializers.CharField(required=True, max_length=254, error_messages={
                                        "required": "The re password field is required", "blank": "The re password field cannot be blank"})




class ReadCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "user_name",
            "is_staff",
            "address",
            "date_joined",
        ]
        read_only_fields = ("is_active", "is_staff")



  
class BlockDeleteUserSerializer(serializers.Serializer):
    user = serializers.UUIDField(required=True)
    action = serializers.CharField(required=True)


class RegisterUserResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class VerifySocialSignupExistsResponseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    access = serializers.CharField()

