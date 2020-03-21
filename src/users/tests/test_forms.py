"""
Form tests
"""

from django.test import tag
from encryption_compendium.test_utils import random_email, random_password, UnitTest
from users.forms import (
    ResearchLoginForm,
    AddNewUserForm,
    SignupForm,
    PasswordChangeForm,
)
from users.models import User


@tag("auth", "login", "forms")
class ResearchLoginFormTestCase(UnitTest):
    """
    Test suite for ResearchLoginForm
    """

    def setUp(self):
        super().setUp()
        self.form_data = {"username": self.username, "password": self.password}

    def test_login(self):
        User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        ).save()
        form = ResearchLoginForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_login(self):
        # Try to log in as a nonexistent user
        form = ResearchLoginForm(data=self.form_data)
        self.assertFalse(form.is_valid())

        # Try to log in as a deactivated user
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        form = ResearchLoginForm(data=self.form_data)
        self.assertTrue(form.is_valid())

        user.is_active = False
        user.save()

        form = ResearchLoginForm(data=self.form_data)
        self.assertFalse(form.is_valid())

        # Try to log in with an invalid password
        data = {"username": self.username, "password": random_password(self.rd)}
        form = ResearchLoginForm(data=data)
        self.assertFalse(form.is_valid())


class AddNewUserFormTestCase(UnitTest):
    """
    Test suite for AddNewUserForm
    """

    def setUp(self):
        super().setUp(create_user=True)

    def test_validate_new_user(self):
        data = {"email": random_email(self.rd)}
        self.assertTrue(AddNewUserForm(data=data).is_valid())

    def test_invalid_user_email(self):
        data = {"email": "hello, world"}
        self.assertFalse(AddNewUserForm(data=data).is_valid())
        data = {"email": "user123@"}
        self.assertFalse(AddNewUserForm(data=data).is_valid())

        # Email must be specified
        self.assertFalse(AddNewUserForm(data={}).is_valid())

        # The email cannot already be in use by a user on the site.
        data = {"email": self.email}
        self.assertFalse(AddNewUserForm(data=data).is_valid())


class SignUpFormTestCase(UnitTest):
    """
    Test suite for SignupForm
    """

    def setUp(self):
        super().setUp()
        self.data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "password_2": self.password,
        }

    def test_validate_new_user(self):
        self.assertTrue(SignupForm(data=self.data).is_valid())

    def test_passwords_must_match(self):
        self.data["password_2"] = random_password(self.rd)
        self.assertFalse(SignupForm(data=self.data).is_valid())


@tag("auth", "forms", "password-change")
class ChangePasswordFormTestCase(UnitTest):
    """
    Test suite for ChangePasswordForm
    """

    def setUp(self):
        super().setUp(preauth=True)

    def test_password_change(self):
        """
        Ensure that the ChangePasswordForm correctly validates the user input
        when they enter their original password, and the new passwords match.
        """
        newpass = random_password(self.rd)
        data = {
            "oldpassword": self.password,
            "newpassword1": newpass,
            "newpassword2": newpass,
        }
        form = PasswordChangeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_changing_to_weak_password(self):
        """
        The form should not be validated when the user tries to use a weak
        password.
        """
        weak_pass = "password12345"
        data = {
            "oldpassword": self.password,
            "newpassword1": weak_pass,
            "newpassword2": weak_pass,
        }
        form = PasswordChangeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_passwords_do_not_match(self):
        """
        The form should be invalidated when the user enters two different
        passwords.
        """
        newpass1 = "ed3447ba-2a94-4a58-b5ae-90b8d64aa292"
        newpass2 = "06fe3a38-09cb-43aa-a87b-f06cbb43c787"
        data = {
            "oldpassword": self.password,
            "newpassword1": newpass1,
            "newpassword2": newpass2,
        }
        form = PasswordChangeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_same_old_and_new_password(self):
        """
        Form should be invalidated when the new password is the same as the
        old password.
        """
        data = {
            "oldpassword": self.password,
            "newpassword1": self.password,
            "newpassword2": self.password,
        }
        form = PasswordChangeForm(data=data)
        self.assertFalse(form.is_valid())
