from django.test import tag
from encryption_compendium.test_utils import UnitTest

"""
---------------------------------------------------
Tests for the login view
---------------------------------------------------
"""


@tag("auth")
class LoginTest(UnitTest):
    def test_login_as_existing_user(self):
        pass
