from django.contrib.auth import get_user
from django.test import tag
from encryption_compendium.test_utils import UnitTest
from research_assistant.models import User

"""
---------------------------------------------------
Custom user model tests
---------------------------------------------------
"""


@tag("auth", "users")
class UserModelTestCase(UnitTest):
    def test_create_new_user(self):
        user = User.objects.create_user(email=self.email, password=self.password)

        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

        # Test User defaults
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

        # We should now be able to login as the new user
        self.client.login(email=self.email, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertEqual(get_user(self.client), user)

    @tag("admin")
    def test_create_new_superuser(self):
        user = User.objects.create_superuser(email=self.email, password=self.password)

        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

        # Test superuser defaults
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    def test_can_disable_users(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        self.assertTrue(user.is_active)

        # Should be able to log in when user.is_active is True
        result = self.client.login(email=self.email, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)

        # Deactivate the user. The open session should be closed, and it
        # should be impossible to login as the disabled user.
        user.is_active = False
        user.save()

        self.client.logout()
        self.assertFalse(get_user(self.client).is_authenticated)

        self.client.login(email=self.email, password=self.password)
        self.assertFalse(get_user(self.client).is_authenticated)
