from base64 import b64encode
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import tag
from django.urls import reverse
from utils.test_utils import UnitTest, random_password
from users.models import User
from secrets import token_bytes

"""
---------------------------------------------------
Test that the project settings are set correctly
---------------------------------------------------
"""


@tag("settings")
class ProjectSettingsTestCase(UnitTest):
    @tag("auth", "login", "logout")
    def test_login_logout_redirect_urls(self):
        self.assertEqual(settings.LOGIN_URL, reverse("research login"))
        self.assertEqual(settings.LOGIN_REDIRECT_URL, reverse("research dashboard"))
        self.assertEqual(settings.LOGOUT_REDIRECT_URL, reverse("research login"))


"""
---------------------------------------------------
Test settings for user password
---------------------------------------------------
"""


@tag("settings", "auth")
class PasswordSettingsTestCase(UnitTest):
    def test_password_invalidation(self):
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password,
        )

        min_len = settings.MIN_PASSWORD_LENGTH
        max_len = settings.MAX_PASSWORD_LENGTH

        # Password too short
        password = random_password(self.rd)[: min_len - 1].encode("utf-8")
        with self.assertRaises(ValidationError):
            validate_password(password)

        # Password too long
        password = b64encode(token_bytes(200))[: max_len + 1]
        with self.assertRaises(ValidationError):
            validate_password(password)

        # Password is too similar to user information
        with self.assertRaises(ValidationError):
            validate_password(password, user=user)

        # Password is too common
        with self.assertRaises(ValidationError):
            validate_password("password12345")
        with self.assertRaises(ValidationError):
            validate_password("1234567890")
