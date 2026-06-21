import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexPasswordValidator:
    def validate(self, password, user=None):
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Your password must contain at least one uppercase letter (A-Z)."),
                code='password_no_upper',
            )

        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Your password must contain at least one number (0-9)."),
                code='password_no_number',
            )

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Your password must contain at least one special character (e.g., @, #, $, %)."),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter, one number, and one special character.")