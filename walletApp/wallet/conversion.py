from typing import AnyStr, Union, Dict
from urllib import response
from django.conf import settings
import requests
from decimal import Decimal
from django.utils import timezone
import os



class BaseConversionProvider:
    def convert(self) -> Union[bool, Dict]:
        ...

class APILayerIntegration(BaseConversionProvider):
    
    BASE_URL = "https://api.exchangeratesapi.io/v1/"
    API_KEY = os.environ.get('APILAYER_KEY')

    def convert(
        self, convert_from: str, convert_to: str, amount: int, **kwargs
    ) -> Union[bool, Dict]:

        if convert_from == 'NGN' and convert_to == 'USD':
            converted = float(amount) * float(0.0022)
        elif convert_from == 'USD' and convert_to == 'NGN':
            converted = float(amount) * float(455.06)
        else:
            return False, "not in conversion list"

        return True, converted
        
        # url = f"{self.BASE_URL}convert"
        # HEADERS = {
        #     "access_key": self.API_KEY
        # }
        # params = {
        #     "access_key": self.API_KEY,
        #     "from": convert_from,
        #     "to": convert_to,
        #     "amount": amount
        # }

        # resp = requests.get(url=url, params=params, headers=HEADERS)
        # print(resp.url)

        # if resp.status_code == 200:
        #     return True, resp.json().get('info').get('rate')
        # else:
        #     return False, resp.json()

    

class ConversionProvider(BaseConversionProvider):
    def __init__(self, provider=APILayerIntegration) -> None:
        self.provider = provider()

    def convert(
        self, convert_from: str, convert_to: str, amount: str, **kwargs
    ) -> Union[bool, Dict]:

        return self.provider.convert(convert_from, convert_to, amount, **kwargs)

    