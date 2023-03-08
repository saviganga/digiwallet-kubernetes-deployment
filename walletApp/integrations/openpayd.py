from typing import AnyStr, Union, Dict
import requests
import os


import requests

url = "https://sandbox.openpayd.com/api/oauth/token?grant_type=client_credentials"

headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "authorization": "Basic dmlzb3BheTooI2UyJm9KRVI4"
}

response = requests.post(url, headers=headers)

print(response.text)



class OpenPaydIntegration:

    BASE_URL = "https://sandbox.openpayd.com/api"
    
    BASE_URL = "https://api.exchangeratesapi.io/v1/"
    API_KEY = os.environ.get('OPENPAYD_KEY')
    USERNAME = os.environ.get('OPENPAYD_USERNAME')

    AUTH_URL = f"{BASE_URL}/oauth/token?grant_type=client_credentials"

    HEADERS = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "authorization": "Basic dmlzb3BheTooI2UyJm9KRVI4"
    }

    def get_auth(self):

        response = requests.post(self.AUTH_URL, headers=self.HEADERS)
        auth_id = response.json()['accountHolderId']
        return auth_id



class PayD(OpenPaydIntegration):
    def __init__(self, provider=OpenPaydIntegration) -> None:
        self.provider = provider()

    def get_auth(
        self, 
    ):

        return self.provider.get_auth()











url = "https://sandbox.openpayd.com/api/oauth/token?grant_type=client_credentials"

headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(url, headers=headers)

print(response.text)