from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token podobny do tego z resetu hasła, ale związany też z is_verified.
    Dzięki temu po potwierdzeniu maila stary link przestaje być ważny.
    """
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_verified}"

email_verification_token = EmailVerificationTokenGenerator()

class PasswordResetTokenGeneratorExt(PasswordResetTokenGenerator):
    """
    Oddzielny generator do resetu hasła.
    Można użyć identycznie jak wbudowany, tu tylko trzymamy go pod własną nazwą.
    """
    def _make_hash_value(self, user, timestamp):
        # Możesz to zostawić jak w bazowym albo dopasować do swoich potrzeb
        return f"{user.pk}{timestamp}{user.is_active}{user.last_login}"
        
password_reset_token = PasswordResetTokenGenerator()