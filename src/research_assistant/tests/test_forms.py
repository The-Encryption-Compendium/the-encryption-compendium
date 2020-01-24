from django.test import tag
from encryption_compendium.test_utils import UnitTest, random_password
from research_assistant.forms import ResearchLoginForm
from research_assistant.models import User

"""
---------------------------------------------------
Login form tests
---------------------------------------------------
"""


@tag("auth", "login", "forms")
class ResearchLoginFormTestCase(UnitTest):
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
