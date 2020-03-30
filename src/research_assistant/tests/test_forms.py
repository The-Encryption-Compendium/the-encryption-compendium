import io
import os
import random

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag
from utils.test_utils import UnitTest
from research_assistant.forms import BibTexUploadForm, JsonUploadForm

"""
---------------------------------------------------
Entry upload form tests
---------------------------------------------------
"""


@tag("compendium-entries", "forms")
class JsonUploadFormTestCase(UnitTest):
    """
    Test cases for adding a new compendium entry via JSON upload
    """

    def setUp(self):
        self.test_filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "test_data.json"
        )
        with open(self.test_filename, "r") as f:
            self.json = f.read()
        self.json_file = SimpleUploadedFile(
            self.test_filename, self.json.encode("utf-8")
        )

        self.form = JsonUploadForm(
            data={"json_file": self.test_filename}, files={"json_file": self.json_file}
        )

        # Check that JsonUploadForm is correctly validating the file
        self.assertTrue(self.form.is_valid())
        self.data = self.form.cleaned_data["json_file"]
        self.assertEqual(len(self.data), 3)

    def test_titles(self):
        self.assertEqual(
            self.data[0]["title"],
            "Australian Government Passes Contentious Encryption Law",
        )
        self.assertEqual(
            self.data[1]["title"],
            "A Judicial Framework for Evaluating Network Investigative Techniques",
        )
        self.assertEqual(
            self.data[2]["title"],
            "American Cryptography during the Cold War, 1945-1989",
        )

    def test_abstracts(self):
        self.assertTrue(self.data[0]["abstract"].startswith("The law, opposed by "))
        self.assertTrue(
            self.data[1]["abstract"].startswith("At Motherboard, Joseph Cox")
        )
        self.assertEqual(self.data[2]["abstract"], None)

    def test_dates(self):
        self.assertEqual(self.data[0]["year"], 2018)
        self.assertEqual(self.data[0]["month"], 12)
        self.assertEqual(self.data[0]["day"], 6)

    def test_urls(self):
        self.assertEqual(
            self.data[0]["url"],
            "https://www.nytimes.com/2018/12/06/world/australia/encryption-bill-nauru.html",
        )

    def test_authors(self):
        self.assertEqual(self.data[0]["authors"], ["Jamie Tarabay"])
        self.assertEqual(
            self.data[1]["authors"], ["Susan Hennessey", "Nicholas Weaver"]
        )
        self.assertEqual(
            self.data[2]["authors"], ["National Security Agency"],
        )


@tag("compendium-entries", "forms")
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
