from django.test import tag
from encryption_compendium.test_utils import UnitTest, random_password
from research_settings.forms import PasswordChangeForm

"""
Settings form tests
"""


@tag("auth", "forms", "password-change")
class ResearchChangePasswordFormTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

    def test_change_password(self):
        # try to change user password
        new_password = random_password(self.rd)
        data = {
            "oldpassword": self.password,
            "newpassword1": new_password,
            "newpassword2": new_password,
        }
        form = PasswordChangeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_passwords_do_not_match(self):
        # try to enter different passwords in new and confirm password fields
        data = {
            "oldpassword": self.password,
            "newpassword1": random_password(self.rd),
            "newpassword2": random_password(self.rd),
        }
        form = PasswordChangeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_same_old_and_new_password(self):
        # try to change password to current password
        data = {
            "oldpassword": self.password,
            "newpassword1": self.password,
            "newpassword2": self.password,
        }
        form = PasswordChangeForm(data=data)
        self.assertFalse(form.is_valid())
