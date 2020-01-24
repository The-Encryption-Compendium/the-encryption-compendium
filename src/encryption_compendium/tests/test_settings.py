from django.conf import settings
from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import UnitTest

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
