from django import db
from django.contrib.auth import get_user
from django.test import tag
from django.utils import timezone
from encryption_compendium.test_utils import UnitTest, random_password
from research_assistant.models import User, CompendiumEntry, CompendiumEntryTag

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


"""
---------------------------------------------------
CompendiumEntryTag model tests
---------------------------------------------------
"""


class CompendiumEntryTagModelTestCase(UnitTest):
    @tag("tmp")
    def test_create_new_tag(self):
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 0)
        new_tag = CompendiumEntryTag.objects.create(tagname="my-new-tag")
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 1)
        self.assertEqual(new_tag.tagname, "my-new-tag")

        # Tag names should be unique. This is how we ensure that we can identify
        # pairs of CompendiumEntries that share the same tags.
        with self.assertRaises(db.utils.IntegrityError):
            CompendiumEntryTag.objects.create(tagname="my-new-tag")


"""
---------------------------------------------------
CompendiumEntry model tests
---------------------------------------------------
"""


class CompendiumEntryModelTestCase(UnitTest):
    def setUp(self):
        super().setUp()
        self.title = self.username
        self.abstract = "This is the abstract of our resource"
        self.url = "https://example.com"

    def test_create_resource(self):
        entry = CompendiumEntry.objects.create(
            title=self.title, abstract=self.abstract, url=self.url
        )
        self.assertEqual(entry.title, self.title)
        self.assertEqual(entry.abstract, self.abstract)
        self.assertEqual(entry.url, self.url)
        self.assertEqual(entry.owner_id, None)
        self.assertTrue((timezone.now() - entry.date_added).seconds < 10)

        # URL and abstract fields can be blank
        entry = CompendiumEntry.objects.create(title=self.title)
        self.assertEqual(entry.abstract, None)
        self.assertEqual(entry.url, None)

    def test_attempt_create_resource_with_invalid_fields(self):
        # TODO: empty title
        # TODO: URL not actually a URL
        # TODO: fields exceed maximum lengths
        pass
