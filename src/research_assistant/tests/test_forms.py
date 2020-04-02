import io
import os
import random

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag
from research_assistant.forms import BibTexUploadForm, JsonUploadForm
from utils.test_utils import UnitTest
from unittest import skip

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
        self.form.is_valid()
        self.assertTrue(self.form.is_valid())
        self.data = [subform.cleaned_data for subform in self.form.cleaned_data]
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

    @skip("TODO")
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

        self.form = BibTexUploadForm(
            data={"bibtex_file": self.test_filename},
            files={"bibtex_file": self.bibfile},
        )
        self.assertTrue(self.form.is_valid())

        # Ensure that the cleaned data are in the correct format
        self.results = self.form.cleaned_data
        self.assertTrue(isinstance(self.results, list))
        self.assertTrue(all(isinstance(r, dict) for r in self.results))
        self.assertEqual(len(self.results), 2)

        # Within the ith dictionary there should be the following:
        # - A CompendiumEntryForm with data for the ith entry
        # - A list of authors
        # - A list of tags
        self.assertTrue(all(len(r.keys()) == 3 for r in self.results))
        for key in ("form", "authors", "tags"):
            self.assertTrue(all(key in r for r in self.results))

        self.data = [r["form"].cleaned_data for r in self.results]

    def test_forms_are_validated(self):
        """Each CompendiumEntryForm should be valid"""
        self.assertTrue(all(r["form"].is_valid() for r in self.results))

    def test_titles_are_parsed_correctly(self):
        self.assertTrue(self.data[0]["title"].startswith("A Judicial Framework"))
        self.assertTrue(self.data[1]["title"].startswith("A Flawed Encryption Policy"))

    def test_abstracts_are_parsed_correctly(self):
        self.assertTrue(self.data[0]["abstract"].startswith("At Motherboard"))
        self.assertTrue(self.data[1]["abstract"].startswith("An editorial"))

    def test_dates_are_parsed_correctly(self):
        self.assertEqual(self.data[0]["month"], 7)
        self.assertEqual(self.data[0]["year"], 2016)
        self.assertEqual(self.data[1]["month"], 4)
        self.assertEqual(self.data[1]["year"], 1996)

    def test_authors_are_parsed_correctly(self):
        self.assertEqual(
            self.results[0]["authors"], ["Susan Hennessey", "Nicholas Weaver"]
        )
        self.assertEqual(self.results[1]["authors"], ["Anonymous"])

    def test_tags_are_parsed_correctly(self):
        self.assertEqual(self.results[0]["tags"], ["2010s", "Child Exploitation"])
        self.assertEqual(self.results[1]["tags"], [])
