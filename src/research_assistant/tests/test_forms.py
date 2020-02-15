from django.test import tag
from encryption_compendium.test_utils import random_email, random_password, UnitTest
from research_assistant.forms import (
    AddNewUserForm,
    ResearchLoginForm,
    CompendiumEntryForm,
    NewTagForm,
    SignupForm,
)
from research_assistant.models import User, CompendiumEntryTag

"""
---------------------------------------------------
Auth-related forms
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


class AddNewUserFormTestCase(UnitTest):
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


class SignUpFormTestCase(UnitTest):
    def test_validate_new_user(self):
        data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "password_2": self.password,
        }
        self.assertTrue(SignupForm(data=data).is_valid())

"""
---------------------------------------------------
Entry upload form tests
---------------------------------------------------
"""


@tag("compendium-entries")
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


"""
---------------------------------------------------
Form to add new tags
---------------------------------------------------
"""


@tag("compendium-entries")
class NewTagFormTestCase(UnitTest):
    def setUp(self):
        super().setUp()

    def test_add_new_tag_to_the_database(self):
        # By default, there shouldn't be any tags in the database
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 0)

        # Add a new tag view the NewTagForm
        form = NewTagForm(data={"tagname": "my test tag"})
        self.assertTrue(form.is_valid())
        form.save()

        # The new tag should now be saved to the database
        tags = CompendiumEntryTag.objects.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].tagname, "my test tag")

    def test_add_invalid_tag_to_the_database(self):
        ### Try to double-add a tag
        tag = CompendiumEntryTag(tagname="test-tag").save()

        form = NewTagForm(data={"tagname": "test-tag"})
        self.assertFalse(form.is_valid())

        ### Try to add an empty tag
        form = NewTagForm(data={"tagname": ""})
        self.assertFalse(form.is_valid())

    def test_tags_are_case_insensitive(self):
        # Tags should be case-insensitive, e.g. 'Encryption' should be the same
        # as 'encryption'. When adding a new tag through this form, ensure that
        # the tags are automatically de-capitalized.

        # Add a new tag via the NewTagForm
        form = NewTagForm(data={"tagname": "ENCRYPTION"})
        self.assertTrue(form.is_valid())
        form.save()

        tags = CompendiumEntryTag.objects.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].tagname, "encryption")

        # Attempt to add a new tag with the same name (but different
        # capitalization).
        form = NewTagForm(data={"tagname": "Encryption"})
        self.assertFalse(form.is_valid())
