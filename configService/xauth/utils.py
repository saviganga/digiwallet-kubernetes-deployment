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
    print(f"{JWT_SECRET_KEY}\n{JWT_CODE}")

    def authentication_appDBquery(self, query):
        """
            Return all rows from a cursor as a namedtuple
            https://docs.djangoproject.com/en/3.2/topics/db/sql/
        """
        with connections['auth'].cursor() as cursor:
            cursor.execute(query)
            desc = cursor.description
            nt_result = namedtuple('Result', [col[0] for col in desc])
            return [nt_result(*row) for row in cursor.fetchall()]

    def validate_token(self, jwt_token):
        valid_token = jwt_token.split(' ')[1]
        print(valid_token)

        try:
            print('try')
            try:
                userData = jwt.decode(valid_token, self.JWT_SECRET_KEY, algorithms=[self.JWT_CODE])
                print(userData)
            except Exception as userdataerror:
                print('userdataerror:\n')
                print(userdataerror)
            userId = userData.get('sub')
            is_user, valid_user = self.find_user(userId)

            if not is_user:
                return False, valid_user
                
            if valid_user:                    
                return True, valid_user
            else:
                return False, "User does not exist"

        except Exception as e:
            print('except')
            print(e)
            return False, "error"

    def find_user(self,userId):
    
        try:
            query = f"SELECT * FROM public.user_customuser WHERE id='{userId}';"

            user = self.authentication_appDBquery(query=query)
                        
            return True, user[0]
        except Exception as e:
            print(e)
            return False, 'Cannot find user'

    



connect = ConnectDB()
