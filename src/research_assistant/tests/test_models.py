from datetime import date
from django import db
from django.contrib.auth import get_user
from django.test import tag
from django.utils import timezone
from encryption_compendium.test_utils import UnitTest, random_password, random_username
from random import randrange
from entries.models import (
    CompendiumEntry,
    CompendiumEntryTag,
)
from users.models import SignupToken, User

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
        self.assertTrue((timezone.now() - user.date_joined).seconds < 30)

        # Test User defaults
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        # We should now be able to login as the new user
        self.client.login(username=self.username, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertEqual(get_user(self.client), user)

    def test_create_new_superuser(self):
        user = User.objects.create_superuser(
            username=self.username, email=self.email, password=self.password
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)
        self.assertTrue((timezone.now() - user.date_joined).seconds < 30)

        # Login as the user
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
        self.assertTrue(user.is_staff)

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
