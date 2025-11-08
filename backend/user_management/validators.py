from django.core.exceptions import ValidationError
import re


class StrongPasswordValidator:
    """
    Checks that the password contains at least:
    - one uppercase letter
    - one digit
    - one special character
    """

    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError("The password must contain at least one uppercase letter.")

        if not re.search(r"\d", password):
            raise ValidationError("The password must contain at least one digit.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("The password must contain at least one special character (!@#$%^&* etc.).")

    def get_help_text(self):
        return (
            "Password must contain at least one uppercase letter, one digit, and one special character."
        )
