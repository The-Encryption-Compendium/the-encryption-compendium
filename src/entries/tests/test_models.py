"""
Tests for models in the 'entries' app
"""

from datetime import date
from django import db
from django.utils import timezone
from entries.models import CompendiumEntry, CompendiumEntryTag
from encryption_compendium.test_utils import UnitTest, random_username
from random import randrange


class CompendiumEntryModelTestCase(UnitTest):
    """
    Test suite for the CompendiumEntryModel
    """

    def setUp(self):
        super().setUp()
        self.title = self.username
        self.abstract = "This is the abstract of our resource"
        self.url = "https://example.com"
        self.year = randrange(1900, date.today().year)
        self.month = randrange(1, 12)
        self.day = randrange(1, 31)
        self.publisher = random_username(self.rd)

    def test_create_resource(self):
        entry = CompendiumEntry.objects.create(
            title=self.title,
            abstract=self.abstract,
            url=self.url,
            year=self.year,
            month=self.month,
            day=self.day,
        )
        self.assertEqual(entry.title, self.title)
        self.assertEqual(entry.abstract, self.abstract)
        self.assertEqual(entry.url, self.url)
        self.assertEqual(entry.owner_id, None)
        self.assertEqual(entry.year, self.year)
        self.assertEqual(entry.month, self.month)
        self.assertEqual(entry.day, self.day)
        self.assertTrue((timezone.now() - entry.date_added).seconds < 10)

        # URL, abstract, year, month, and day fields can be blank
        entry = CompendiumEntry.objects.create(title=self.title)
        self.assertEqual(entry.abstract, None)
        self.assertEqual(entry.url, None)

    def test_attempt_create_resource_with_invalid_fields(self):
        # TODO: empty title
        # TODO: URL not actually a URL
        # TODO: fields exceed maximum lengths
        pass


class CompendiumEntryTagModelTestCase(UnitTest):
    """
    Model tests for CompendiumEntryTag
    """

    def test_create_new_tag(self):
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 0)
        new_tag = CompendiumEntryTag.objects.create(tagname="my-new-tag")
        self.assertEqual(len(CompendiumEntryTag.objects.all()), 1)
        self.assertEqual(new_tag.tagname, "my-new-tag")

        # Tag names should be unique. This is how we ensure that we can identify
        # pairs of CompendiumEntries that share the same tags.
        with self.assertRaises(db.utils.IntegrityError):
            CompendiumEntryTag.objects.create(tagname="my-new-tag")
