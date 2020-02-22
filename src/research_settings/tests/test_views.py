from django.contrib.auth import get_user
from django.test import tag
from django.urls import reverse
from encryption_compendium.test_utils import random_username, random_password, UnitTest
from research_assistant.models import User

"""
---------------------------------------------------
Tests for the password change
---------------------------------------------------
"""


class ChangePasswordTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

    def test_logout_on_password_change(self):
        response = self.client.get(reverse("research settings"))
        self.assertTemplateUsed(response, "base.html")
        # try to change password with correct credentials
        newpassword = random_password(self.rd)
        data = {
            "oldpassword": self.password,
            "newpassword1": newpassword,
            "newpassword2": newpassword,
        }

        self.client.post(reverse("research settings"), data)

        self.assertFalse(get_user(self.client).is_authenticated)

    def test_failed_pass_change_with_incorrect_old_password(self):
        oldpassword = random_password(self.rd)
        newpassword = random_password(self.rd)

        data = {
            "oldpassword": oldpassword,
            "newpassword1": newpassword,
            "newpassword2": newpassword,
        }

        self.client.post(reverse("research settings"), data)

        self.assertTrue(get_user(self.client).is_authenticated)
