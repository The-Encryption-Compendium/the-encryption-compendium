import datetime
import os
import random
import string

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag
from encryption_compendium.test_utils import (
    random_email,
    random_password,
    UnitTest,
    random_username,
)
from research_assistant.forms import (
    BibTexUploadForm,
    CompendiumEntryForm,
    NewTagForm,
)
from entries.models import CompendiumEntryTag
from users.forms import (
    AddNewUserForm,
    ResearchLoginForm,
    SignupForm,
    PasswordChangeForm,
)
from users.models import SignupToken, User


"""
---------------------------------------------------
Entry upload form tests
---------------------------------------------------
"""


@tag("compendium-entries", "tags")
class CompendiumEntryFormTestCase(UnitTest):
    """
    Test for the CompendiumEntryForm, which serves as the interface for creating
    and end editing compendium entries.
    """

    def setUp(self):
        super().setUp()

        # Create some example tags for testing
        self.tag_ids = []
        for tagname in ("test_tag_A", "test_tag_B", "test_tag_C"):
            if not CompendiumEntryTag.objects.filter(tagname=tagname).exists():
                new_tag = CompendiumEntryTag.objects.create(tagname=tagname)
                self.tag_ids.append(new_tag.id)

        self.title = random_password(self.rd)
        self.abstract = random_password(self.rd)
        self.url = "https://example.com"
        self.data = {
            "title": self.title,
            "abstract": self.abstract,
            "url": self.url,
            "tags": [self.tag_ids[0]],
        }

    def test_submit_new_entry(self):
        form = CompendiumEntryForm(data=self.data)
        result = form.is_valid()
        self.assertTrue(form.is_valid())

    def test_submit_entry_with_invalid_title(self):
        """
        Ensure that CompendiumEntryForm does not validate data with invalid
        titles.
        """
        # Try to create an entry without a title
        data = self.data
        data.pop("title")
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

        # Try to create an entry with a blank title
        data = self.data
        data["title"] = ""
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

    def test_submit_entry_with_invalid_url(self):
        """
        The CompendiumEntryForm should invalidate inputs that have an
        invalid URL field.
        """
        data = self.data
        data["url"] = "not a valid URL"
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

    def test_submit_entry_invalid_tags(self):
        """
        The CompendiumEntryForm should enforce that inputs have at
        least one tag, and that tags already exist in the database.
        """
        ### Try to submit data without any tags
        data = self.data
        data.pop("tags")
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

        ### Try to submit data with tags that don't exist
        invalid_tag_id = max(self.tag_ids) + 1
        data = self.data
        data["tags"] = [invalid_tag_id]
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

    def test_entry_with_publisher_field(self):
        # Test publisher field with valid input
        data = self.data
        data["publisher_text"] = random_username(self.rd)
        self.assertTrue(CompendiumEntryForm(data=data).is_valid())

    def test_form_correctly_validates_date_field(self):
        """
        Ensure that the CompendiumEntryForm successfully validates correct dates.
        In addition, it should clean each of its fields correctly, e.g. it should
        store 'None' for the day field when the day is not specified.
        """

        ### The form should be able to handle a full day/month/year specification
        data = self.data.copy()
        data["day"] = 15
        data["month"] = 8
        data["year"] = 2000
        self.assertTrue(CompendiumEntryForm(data=data).is_valid())

        ### The form should be able to handle a month/year specification without
        ### selecting a day.
        data.pop("day")
        form = CompendiumEntryForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get("day"), None)

        ### The form should be able to handle a year specification without either
        ### a day or month.
        data.pop("month")
        form = CompendiumEntryForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get("day"), None)
        self.assertEqual(form.cleaned_data.get("month"), None)

    def test_form_invalidates_bad_dates(self):
        """
        The form should invalidate dates that aren't correct, e.g. June 31st.
        In addition, we need to enforce that the year of publication is selected
        if the month is selected, and that both month and year are selected if the
        day of publication has been specified.
        """

        # Ensure that the base data are okay
        data = self.data
        self.assertTrue(CompendiumEntryForm(data=data).is_valid())

        ### We cannot provide invalid dates (e.g. June 31) to the form
        data = self.data.copy()
        data["day"] = 31
        data["month"] = 6
        data["year"] = 2005
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

        data["day"] = 29
        data["month"] = 2
        data["year"] = 1900
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())

        ### A form with the day specified must also have the month and year
        data = self.data.copy()
        data["day"] = 1
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())
        data["month"] = 1
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())
        data["year"] = 2000
        self.assertTrue(CompendiumEntryForm(data=data).is_valid())

        ### A form with the month specified must also have its year
        data = self.data.copy()
        data["month"] = 1
        self.assertFalse(CompendiumEntryForm(data=data).is_valid())
        data["year"] = 2000
        self.assertTrue(CompendiumEntryForm(data=data).is_valid())


@tag("compendium-entries")
class BibTexCompendiumEntryUploadTestCase(UnitTest):
    """
    Test cases for adding a new compendium entry using BibTeX.
    """

    def setUp(self):
        super().setUp()

        self.test_filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "test_data.bib"
        )
        with open(self.test_filename, "r") as f:
            self.bib = f.read()
            self.bibfile = SimpleUploadedFile(
                self.test_filename, self.bib.encode("utf-8"),
            )

    def test_both_upload_methods_work_correctly(self):
        """
        Test the results of uploading the data manually versus uploading a
        .bib file with all of the required data. Both methods should generate
        the same results.
        """
        ### Form should be valid when entering data manually
        manual_form = BibTexUploadForm(data={"bibtex_entry": self.bib})
        self.assertTrue(manual_form.is_valid())

        ### Form should be valid when uploading a .bib file
        bibfile_form = BibTexUploadForm(
            data={"bibtex_file": self.test_filename},
            files={"bibtex_file": self.bibfile},
        )
        self.assertTrue(bibfile_form.is_valid())

        ### Both forms should create the same results
        self.assertEqual(
            manual_form.cleaned_data.get("bibtex"),
            bibfile_form.cleaned_data.get("bibtex"),
        )

        ### Manually check that the BibTeX was parsed correctly
        bibtex = manual_form.cleaned_data.get("bibtex")
        self.assertEqual(len(bibtex), 2)
        self.assertTrue("susan_hennessey_judicial_2016" in bibtex)
        self.assertTrue("anonymous_flawed_1996" in bibtex)

        entry = bibtex["susan_hennessey_judicial_2016"]
        self.assertEqual(entry.get("year"), "2016")
        self.assertEqual(entry.get("month"), "July")
        self.assertEqual(entry.get("journal"), "Lawfare")

        entry = bibtex["anonymous_flawed_1996"]
        self.assertEqual(entry.get("year"), "1996")
        self.assertEqual(entry.get("month"), "April")
        self.assertEqual(entry.get("journal"), "New York Times")

    def test_form_cannot_be_completely_blank(self):
        """
        At least one of the two fields (the .bib file upload or the BibTeX
        textarea) must be non-empty.
        """
        form = BibTexUploadForm()
        self.assertFalse(form.is_valid())

    def test_cannot_use_both_upload_methods_simultaneously(self):
        """
        The user should be able to upload a BibTeX file, or enter BibTeX
        manually, but not both.
        """
        form = BibTexUploadForm(
            data={"bibtex_entry": self.bib, "bibtex_file": self.test_filename},
            files={"bibtex_file": self.bibfile},
        )
        self.assertFalse(form.is_valid())


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
