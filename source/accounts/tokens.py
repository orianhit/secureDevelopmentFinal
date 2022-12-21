from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomTokenGenerator(PasswordResetTokenGenerator):
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """
    key_salt = "accounts.CustomTokenGenerator"
    algorithm = 'sha1'


custom_token_generator = CustomTokenGenerator()
