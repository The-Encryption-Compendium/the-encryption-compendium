from encryption_compendium.test_utils import UnitTest
from django.test import tag

# Create your tests here.


@tag("auth")
class LoginTest(UnitTest):
    def test_login_as_existing_user(self):
        pass
