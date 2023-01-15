from unicodedata import category
from django.db import connections
from collections import namedtuple
import os
import jwt
from dotenv import load_dotenv
from decimal import Decimal
load_dotenv()
from django.utils import timezone
from django.conf import settings
import random
import string
import datetime

import psycopg2
from psycopg2 import Error



class ConnectDB:
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_CODE = os.environ['JWT_CODE']

    def configuration_appDBquery(self, query):
        """
            Return all rows from a cursor as a namedtuple
            https://docs.djangoproject.com/en/3.2/topics/db/sql/
        """
        with connections['config'].cursor() as cursor:
            cursor.execute(query)
            desc = cursor.description
            nt_result = namedtuple('Result', [col[0] for col in desc])
            return [nt_result(*row) for row in cursor.fetchall()]


    
    def validate_country(self,country):
    
        try:
            query = f"SELECT * FROM public.config_country WHERE country='{country}';"

            country = self.configuration_appDBquery(query=query)
                        
            return True, country[0]
        except Exception as e:
            print(e)
            return False, 'Cannot find country'

    



connect = ConnectDB()
