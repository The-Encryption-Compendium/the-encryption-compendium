from django.test import tag
from encryption_compendium.test_utils import UnitTest, random_password
from research_assistant.forms import ResearchLoginForm, CompendiumEntryForm
from research_assistant.models import User, CompendiumEntryTag

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


"""
---------------------------------------------------
Entry upload form tests
---------------------------------------------------
"""


class CompendiumEntryFormTestCase(UnitTest):
    def setUp(self):
        super().setUp()

        self.title = random_password(self.rd)
        self.abstract = random_password(self.rd)
        self.url = "https://example.com"
        self.data = {
            "title": self.title,
            "abstract": self.abstract,
            "url": self.url,
        }

    def test_submit_new_entry(self):
        form = CompendiumEntryForm(data=self.data)
        result = form.is_valid()
        self.assertTrue(form.is_valid())

    def test_submit_entry_with_invalid_fields(self):
        ### Try using invalid values for some of the fields in the form
        # Use an empty title
        data = self.data
        data["title"] = ""
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

        # Use a random string in the URL field (rather than a URL)
        data = self.data
        data["url"] = random_password(self.rd)
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

    def test_submit_entry_with_tags(self):
        ### Submit an entry to the form that uses multiple tags
        # TODO
        pass
