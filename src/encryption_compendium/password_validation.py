from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext as _

"""
---------------------------------------------------
Login form for researchers
---------------------------------------------------
"""


class MaximumLengthValidator:

    def __init__(self, max_length=settings.MAX_PASSWORD_LENGTH):
        self.max_length = max_length

    def validate(self, password, *args):
        if len(password) > self.max_length:
            raise ValidationError(
                _("Password may not contain more than %(max_length)d characters."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password must not contain more than %(max_length)d characters."
            % {"max_length": self.max_length}
        )
