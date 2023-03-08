from pyexpat import model
from rest_framework import serializers
from config import models as config_models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = config_models.Country
        fields = "__all__"


class SupportedCountry(serializers.ModelSerializer):
    country = serializers.CharField(required=True)

    class Meta:
        model = config_models.SupportedCountry
        fields = ["id", "vat_percentage",
                  "platform_fee", "country"]

    def create(self, validated_data):

        country_code = validated_data.get('country')
        try:
            country = config_models.Country.objects.get(country=country_code)
        except Exception as get_country_error:
            print(get_country_error)
            return False, 'Country with this code does not exist'
        validated_data.pop('country')
        validated_data['country'] = country

        try:
            supported_country = self.Meta.model.objects.create(**validated_data)
        except Exception as create_error:
            print(create_error)
            return False, "Unable to create supported country"
        
        return True, supported_country

class ReadSupportedCountrySerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = config_models.SupportedCountry
        fields = ["id", "vat_percentage",
                  "platform_fee", "country"]

    def get_country(self, obj):
        return {
            "id": obj.country.id,
            "country": obj.country.country,
            "currency": obj.country.currency
            }


