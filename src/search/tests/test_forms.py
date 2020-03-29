"""
Tests for forms in the search app
"""

from django.test import tag
from search.forms import BasicSearchForm
from utils.test_utils import UnitTest


@tag("search", "forms")
class BasicSearchFormTest(UnitTest):
    """
    Check that BasicSearchForm correctly valdiates and transforms inputs.
    """

    def setUp(self):
        pass

    def test_extract_words(self):
        """The form should extract unquoted, separated words from queries."""

        query = "hello, world"
        form = BasicSearchForm(data={"query": query})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], ["hello", "world"])

    def test_extract_quoted_strings(self):
        """Test that the form extracts quoted strings from queries."""

        query = '"hello, world!"'
        form = BasicSearchForm(data={"query": query})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], ["hello, world"])

        query = 'a dog, "a cat", a horse'
        form = BasicSearchForm(data={"query": query})
        self.assertTrue(form.is_valid())
        self.assertIn("a cat", form.cleaned_data["query"])
