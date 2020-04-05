"""
Tests for views that are used to modify the compendium.
"""

import os
from django.urls import reverse
from django.test import tag
from entries.models import CompendiumEntry, CompendiumEntryTag, Author
from utils.test_utils import UnitTest


@tag("compendium-modification")
class AddNewCompendiumEntryTestCase(UnitTest):
    """
    Test the view that presents a form for manually creating a new compendium
    entry.
    """

    def setUp(self):
        super().setUp(preauth=True)
        self.new_entry_page = reverse("research new article")

        # Add three tags for testing purposes
        for tagname in ("test_tag_A", "test_tag_B", "test_tag_C"):
            if not CompendiumEntryTag.objects.filter(tagname=tagname).exists():
                CompendiumEntryTag.objects.create(tagname=tagname)

    def test_page_templates(self):
        # Ensure that the page uses the correct templates in its response
        response = self.client.get(self.new_entry_page)
        self.assertTemplateUsed("dashboard_base.html")
        self.assertTemplateUsed("new_article.html")

    @tag("tags")
    def test_add_new_compendium_entry(self):
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        # Retrieve the tag ID for "test_tag_B"
        tag_id = CompendiumEntryTag.objects.get(tagname="test_tag_B").id

        # publisher information
        publisher = random_username(self.rd)

        # published date
        year = random.randrange(1900, datetime.date.today().year)
        month = random.randrange(1, 12)
        day = random.randrange(1, 31)

        # Send POST data to the URL to create a new entry and ensure that
        # the entry was created correctly.
        data = {
            "title": "New compendium entry",
            "abstract": "Abstract for new entry",
            "url": "https://example.com",
            "tags": [tag_id],
            "publisher_text": publisher,
            "year": year,
            "month": month,
            "day": day,
            "edit-entry": "",
        }
        response = self.client.post(self.new_entry_page, data)
        self.assertTrue(len(CompendiumEntry.objects.all()), 1)

        entry = CompendiumEntry.objects.get(title="New compendium entry")
        self.assertEqual(entry.owner, self.user)
        self.assertEqual(entry.title, "New compendium entry")
        self.assertEqual(entry.abstract, "Abstract for new entry")
        self.assertEqual(entry.url, "https://example.com")
        self.assertEqual(len(entry.tags.all()), 1)
        self.assertEqual(entry.tags.get().tagname, "test_tag_B")
        self.assertEqual(entry.publisher.publishername, publisher)
        self.assertEqual(entry.year, year)
        self.assertEqual(entry.month, month)
        self.assertEqual(entry.day, day)

    @tag("tags")
    def test_add_compendium_entry_with_multiple_tags(self):
        """Create a CompendiumEntry with multiple tags"""
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        # Retrieve tag IDs for "test_tag_B" and "test_tag_C"
        id_A = CompendiumEntryTag.objects.get(tagname="test_tag_A").id
        id_C = CompendiumEntryTag.objects.get(tagname="test_tag_C").id

        # Send POST data with multiple tag IDs
        data = {
            "title": "New compendium entry",
            "tags": [id_A, id_C],
            "edit-entry": "",
        }
        self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 1)

        entry = CompendiumEntry.objects.get(title="New compendium entry")
        self.assertEqual(len(entry.tags.all()), 2)
        self.assertTrue(entry.tags.filter(tagname="test_tag_A").exists())
        self.assertFalse(entry.tags.filter(tagname="test_tag_B").exists())
        self.assertTrue(entry.tags.filter(tagname="test_tag_C").exists())

    def test_attempt_to_create_entry_with_empty_title(self):
        """New entries must have a title"""
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)
        tag_id = CompendiumEntryTag.objects.get(tagname="test_tag_A").id

        ### Try to create an entry without a title
        data = {
            "tags": [tag_id],
        }
        response = self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        ### Try to create an entry with an empty title
        data = {
            "title": "",
            "tags": [tag_id],
        }
        response = self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

    def test_attempt_to_create_entry_without_tags(self):
        """New entries must have _at least_ one tag"""
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)

        data = {
            "title": "New compendium entry",
        }
        self.client.post(self.new_entry_page, data)
        self.assertEqual(len(CompendiumEntry.objects.all()), 0)


### TODO


@tag("compendium-modification")
class UploadBibTexViewTestCase(UnitTest):
    """
    Test the view that's involved in handling BibTeX uploads to the site for
    adding new compendium entries.
    """

    def setUp(self):
        super().setUp(preauth=True)

        # Load in a test .bib file
        # self.test_filename = os.
