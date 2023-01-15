import email
from rest_framework import serializers


class JWTAuthSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=True, error_messages={'required': 'Password field is required', 'blank': 'Password field cannot be blank' } )
