from django.contrib.auth import get_user
from django.test import tag
from django.utils import timezone
from encryption_compendium.test_utils import UnitTest, random_password
from research_assistant.models import User

"""
---------------------------------------------------
Custom user model tests
---------------------------------------------------
"""


@tag("auth", "users")
class UserModelTestCase(UnitTest):
    def test_create_new_user(self):
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

        # Test User defaults
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

        # Test User creation time (User should have been created in the last 30
        # seconds).
        current_time = timezone.now()
        created_time = user.date_joined
        delta = current_time - created_time
        self.assertTrue(delta.seconds < 30)

        # We should now be able to login as the new user
        self.client.login(username=self.username, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertEqual(get_user(self.client), user)

    def test_invalid_logins(self):
        # Attempt to login as a nonexistent user
        self.client.login(username=self.username, password=self.password)
        self.assertFalse(get_user(self.client).is_authenticated)

        # Attempt to login as an existing user but with an invalid password
        User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.client.login(username=self.username, password=random_password(self.rd))
        self.assertFalse(get_user(self.client).is_authenticated)

    @tag("admin")
    def test_create_new_superuser(self):
        user = User.objects.create_superuser(
            username=self.username, email=self.email, password=self.password
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

        # Test superuser defaults
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    def test_can_disable_users(self):
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.assertTrue(user.is_active)

        # Should be able to log in when user.is_active is True
        result = self.client.login(username=self.username, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)

        # Deactivate the user. The open session should be closed, and it
        # should be impossible to login as the disabled user.
        user.is_active = False
        user.save()

        self.client.logout()
        self.assertFalse(get_user(self.client).is_authenticated)

        self.client.login(username=self.username, password=self.password)
        self.assertFalse(get_user(self.client).is_authenticated)
