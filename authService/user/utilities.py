
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class AccountActivationToken(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        print(f'\ntimestamp: {timestamp}\n')
        print(text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))
        return(text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))

activation_token = AccountActivationToken()


